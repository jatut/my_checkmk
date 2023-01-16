#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2019 tribe29 GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

# flake8: noqa

import json
import os
import subprocess
from typing import List

import pkg_resources as pkg  # type: ignore[import]
import pytest  # type: ignore[import]
from pipfile import Pipfile  # type: ignore[import]

from tests.testlib import repo_path
from tests.testlib.site import Site

# TODO: Currently we need to invoke pip as a module and cannot use pip3 only.
# This is most likley due to the fact, that we set "PIP_TARGET" in pip3 during intermediate install
# os.environ["PIP_TARGET"] = os.path.join(os.environ["OMD_ROOT"], "local/lib/python3")
PIP_CMD = ["python3", "-m", "pip"]


def _get_import_names_from_dist_name(dist_name: str) -> List[str]:

    # We still have some exceptions to the rule...
    dist_renamings = {
        "repoze-profile": "repoze.profile",
    }

    metadata_dir = pkg.get_distribution(
        dist_renamings.get(dist_name, dist_name)
    ).egg_info  # type: ignore[attr-defined]
    with open("%s/%s" % (metadata_dir, "top_level.txt")) as top_level:
        import_names = top_level.read().rstrip().split("\n")
        # Skip the private modules (starting with an underscore)
        return [name.replace("/", ".") for name in import_names if not name.startswith("_")]


def _get_import_names_from_pipfile() -> List[str]:
    # TODO: There are packages which are currently missing the top_level.txt, so we're hardcoding the import names
    static_import_names = ["typing_extensions"]
    parsed_pipfile = Pipfile.load(filename=repo_path() + "/Pipfile")
    import_names = []
    for dist_name in parsed_pipfile.data["default"].keys():
        if dist_name not in static_import_names:
            import_names.extend(_get_import_names_from_dist_name(dist_name))
    assert import_names
    import_names.extend(static_import_names)
    return import_names


def test_01_python_interpreter_exists(site: Site):
    assert os.path.exists(site.root + "/bin/python3")


def test_02_python_interpreter_path(site: Site):
    p = site.execute(["which", "python3"], stdout=subprocess.PIPE)
    path = p.stdout.read().strip() if p.stdout else "<NO STDOUT>"
    assert path == "/omd/sites/%s/bin/python3" % site.id


def test_03_python_interpreter_version(site: Site):
    p = site.execute(["python3", "-V"], stdout=subprocess.PIPE)
    version = p.stdout.read() if p.stdout else "<NO STDOUT>"
    assert version.startswith("Python 3.9.16")


def test_03_python_path(site: Site):
    p = site.execute(
        ["python3", "-c", "import sys,json; json.dump(sys.path, sys.stdout)"],
        stdout=subprocess.PIPE,
    )
    sys_path = json.loads(p.stdout.read()) if p.stdout else "<NO STDOUT>"

    assert sys_path[0] == ""

    # ordered_path_elements = [
    #    # there may be more, but these have to occur in this order:
    #    site.root + "/local/lib/python3",
    #    site.root + "/lib/python3/plus",
    #    site.root + "/lib/python3.9",
    #    site.root + "/lib/python3",
    # ]
    # TODO: restore this when testing against a daily build > 2022-05-10!
    # assert [s for s in sys_path if s in ordered_path_elements] == ordered_path_elements

    for path in sys_path[1:]:
        assert path.startswith(site.root), f"Found non site path {path!r} in sys.path"


def test_01_pip_exists(site: Site):
    assert os.path.exists(site.root + "/bin/pip3")


def test_02_pip_path(site: Site):
    p = site.execute(["which", "pip3"], stdout=subprocess.PIPE)
    path = p.stdout.read().strip() if p.stdout else "<NO STDOUT>"
    assert path == "/omd/sites/%s/bin/pip3" % site.id


def test_03_pip_interpreter_version(site: Site):
    p = site.execute(["python3", "-m", "pip", "-V"], stdout=subprocess.PIPE)
    version = p.stdout.read() if p.stdout else "<NO STDOUT>"
    assert version.startswith("pip 22.0.4")


@pytest.mark.parametrize(
    "package_name",
    [
        # WARNING:
        # Installing from source takes a long time - and so does the test.
        # So be sure adding new packages here has a real benefit.
        "ibm_db",  # Needed by check_sql: no wheels, so pip must be able to find the Python headers
    ],
)
def test_04_pip_user_can_install_and_uninstall_packages_not_shipped_with_omd(site, package_name):
    p = site.execute(
        PIP_CMD + ["install", "--user", package_name],
        stdout=subprocess.PIPE,
    )
    install_stdout = p.stdout.read()

    assert "Successfully installed" in install_stdout, install_stdout

    for cmd in (
        ["python3", "-c", f"import {package_name}"],
        PIP_CMD + ["uninstall", "-y", package_name],
        PIP_CMD + ["cache", "purge"],
    ):
        p = site.execute(cmd, stdout=subprocess.PIPE)
        p.communicate()
        assert p.returncode == 0


@pytest.mark.parametrize("module_name", _get_import_names_from_pipfile())
def test_python_modules(site: Site, module_name):
    # TODO: Clarify and remove skipping of obscure modules
    # Skip those modules for now, they throw:
    # >       found = self._search_paths(context.pattern, context.path)
    # E       AttributeError: 'Context' object has no attribute 'pattern'
    if module_name in ("jsonschema", "openapi_spec_validator"):
        return
    import importlib  # pylint: disable=import-outside-toplevel

    module = importlib.import_module(module_name)

    # Skip namespace modules, they don't have __file__
    if module.__file__:
        assert module.__file__.startswith(site.root)


def test_python_preferred_encoding():
    import locale  # pylint: disable=import-outside-toplevel

    assert locale.getpreferredencoding() == "UTF-8"
