#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

"""Create and manage user sessions.

When single user sessions are activated, a user an only login once a time. In case a user tries to
login a second time, an error is shown to the later login.

To make this feature possible a session ID is computed during login, saved in the users cookie and
stored in the user profile together with the current time as "last activity" timestamp. This
timestamp is updated during each user activity in the GUI.

Once a user logs out or the "last activity" is older than the configured session timeout, the
session is invalidated. The user can then login again from the same client or another one.
"""

import hmac
import secrets
from dataclasses import asdict
from datetime import datetime
from hashlib import sha256
from typing import Mapping

import cmk.utils.paths
from cmk.utils.site import omd_site
from cmk.utils.type_defs import UserId

import cmk.gui.utils as utils
from cmk.gui.config import active_config
from cmk.gui.exceptions import MKUserError
from cmk.gui.i18n import _
from cmk.gui.log import logger as gui_logger
from cmk.gui.type_defs import SessionInfo
from cmk.gui.userdb.store import convert_session_info, load_custom_attr, save_custom_attr

auth_logger = gui_logger.getChild("auth")


def auth_cookie_name() -> str:
    return f"auth_{omd_site()}"


def auth_cookie_value(username: UserId, session_id: str) -> str:
    return ":".join([username, session_id, generate_auth_hash(username, session_id)])


def generate_auth_hash(username: UserId, session_id: str) -> str:
    """Generates a hash to be added into the cookie value"""
    secret = _load_secret()
    serial = _load_serial(username)
    return hmac.new(
        key=secret, msg=(username + session_id + str(serial)).encode("utf-8"), digestmod=sha256
    ).hexdigest()


def _load_secret() -> bytes:
    """Reads the sites auth secret from a file

    Creates the files if it does not exist. Having access to the secret means that one can issue
    valid cookies for the cookie auth.
    """
    secret_path = cmk.utils.paths.omd_root / "etc" / "auth.secret"
    secret = secret_path.read_bytes() if secret_path.exists() else None

    # Create new secret when this installation has no secret
    #
    # In past versions we used another bad approach to generate a secret. This
    # checks for such secrets and creates a new one. This will invalidate all
    # current auth cookies which means that all logged in users will need to
    # renew their login after update.
    if secret is None or len(secret) == 32:
        secret = secrets.token_bytes(256)
        secret_path.write_bytes(secret)
    return secret


def _load_serial(username: UserId) -> int:
    """Load the password serial of the user

    This serial identifies the current config state of the user account. If either the password is
    changed or the account gets locked the serial is increased and all cookies get invalidated.
    Better use the value from the "serials.mk" file, instead of loading the whole user database via
    load_users() for performance reasons.
    """
    serial = load_custom_attr(user_id=username, key="serial", parser=int)
    return 0 if serial is None else serial


def on_succeeded_login(username: UserId, now: datetime) -> None:
    ensure_user_can_init_session(username, now)
    # Set failed login counter to 0
    save_custom_attr(username, "num_failed_logins", 0)


def ensure_user_can_init_session(username: UserId, now: datetime) -> None:
    """When single user session mode is enabled, check that there is not another active session"""
    session_timeout = active_config.single_user_session
    if session_timeout is None:
        return  # No login session limitation enabled, no validation
    for session_info in load_session_infos(username).values():
        idle_time = now.timestamp() - session_info.last_activity
        if idle_time <= session_timeout:
            auth_logger.debug(
                f"{username} another session is active (inactive for: {idle_time} seconds)"
            )
            raise MKUserError(None, _("Another session is active"))


def load_session_infos(username: UserId, lock: bool = False) -> dict[str, SessionInfo]:
    """Returns the stored sessions of the given user"""
    return (
        load_custom_attr(
            user_id=username, key="session_info", parser=convert_session_info, lock=lock
        )
        or {}
    )


def active_sessions(
    session_infos: Mapping[str, SessionInfo], now: datetime
) -> dict[str, SessionInfo]:
    """Return only valid (not outdated) session

    In single user session mode no sessions are returned. In regular mode, the sessions are limited
    to 20 per user. Sessions with an inactivity > 7 days are also not returned.
    """
    if active_config.single_user_session:
        # In single user session mode there is only one session allowed at a time. Once we
        # reach this place, we can be sure that we are allowed to remove all existing ones.
        return {}

    # NOTE
    # We intentionally don't remove any session which has been logged out, and rely on that fact
    # to be checked elsewhere, because that would lead to the session being removed directly after
    # logout. This would lead to some information in the GUI no longer displaying.
    #
    # Once "last_login" got moved from the session_info struct to the user object, we can clean
    # this up thoroughly.
    return {
        s.session_id: s
        for s in sorted(session_infos.values(), key=lambda s: s.last_activity, reverse=True)[:20]
        if now.timestamp() - s.last_activity < 86400 * 7
    }


def create_session_id() -> str:
    """Creates a random session id for the user and returns it."""
    return utils.gen_id()


def save_session_infos(username: UserId, session_infos: dict[str, SessionInfo]) -> None:
    """Saves the sessions for the current user"""
    save_custom_attr(
        username,
        "session_info",
        repr({k: asdict(v) for k, v in session_infos.items()}),
    )


def is_valid_user_session(
    username: UserId, session_infos: dict[str, SessionInfo], session_id: str
) -> bool:
    """Return True in case this request is done with a currently valid user session"""
    if not session_infos:
        return False  # no session active

    if session_id not in session_infos or session_infos[session_id].logged_out:
        auth_logger.debug(
            "%s session_id %s not valid (logged out or timed out?)", username, session_id
        )
        return False

    return True
