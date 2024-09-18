#!/usr/bin/env bash

# Create a uniform Bazel call to ensure we're using the cache and inject
# system properties to avoid poisonous cache hits.
#
# This might be a workaround, feel free to inform team CI about a more
# sophisitcated way to do this, but we already know, we should take the whole
# build chain into the sandbox - this is just a rough approach.
#
# Run this script e.g. to build the redis build
# ./scripts/run-bazel.sh build @redis//:build
#
# Additional arguments can be passed via the BAZEL_CONFIG_ARGS variable
# BAZEL_CONFIG_ARGS=--config=debug ./scripts/run-bazel.sh build @redis//:build
# or
# ./scripts/run-bazel.sh build --config=debug @redis//:build
#
# Check the check_mk/.bazelrc for available configs
#

set -e

ROOT_DIR="$(dirname "$(dirname "$(realpath "$0")")")"

if ! command -v bazel &>/dev/null; then
    cat <<EOF
bazel command not found in PATH. Please install bazelisk via:
https://github.com/bazelbuild/bazelisk?tab=readme-ov-file#installation

or use the installation script:
./buildscripts/infrastructure/build-nodes/scripts/install-development.sh --profile bazel --only
EOF
    exit 1
fi

ACTION="$1"
TARGET=("${@:2}")
TARGET_S1=$(echo "${TARGET[-1]}" | sed -e 's/\/\///g' -e 's/@//g' -e 's/:/_/g' -e 's/\//_/g')
EXECUTION_LOG_FILE_NAME="${ROOT_DIR}/bazel_execution_log-${TARGET_S1}.json"
BAZEL_CACHE_URL="${BAZEL_CACHE_URL:-bazel-cache.lan.checkmk.net:9092}"

# explicitly create, and later `eval` since run directly with `eval` this script
# would not abort on error
BUILD_ENVIRONMENT="$(
    python3 \
        "${ROOT_DIR}"/scripts/create_build_environment_variables.py \
        "eval:os-release-name:cat /etc/os-release | grep PRETTY | cut -d '\"' -f2" \
        "pathhash:/usr/lib/x86_64-linux-gnu/libc.so" \
        "pathhash:/lib64/libc.so.6" \
        "pathhash:/usr/lib64/libc.so" \
        "pathhash:/opt/gcc-13.2.0"
)"

eval "${BUILD_ENVIRONMENT}"

echo "========================================================================="
echo "Environment variables taken into account by Bazel building \"$*\""
echo "  BAZEL_EXTRA_ARGS: $BAZEL_EXTRA_ARGS"
echo "  SYSTEM_DIGEST: $SYSTEM_DIGEST"
echo
echo "A file ${EXECUTION_LOG_FILE_NAME} will be generated by Bazel containing"
echo "information about caching"
echo "========================================================================="

if [[ -n "${BAZEL_CACHE_URL}" ]]; then
    echo "Bazel remote cache configured to \"${BAZEL_CACHE_URL}\""
    if [ -n "${BAZEL_CACHE_USER}" ] && [ -n "${BAZEL_CACHE_PASSWORD}" ]; then
        echo "Read/Write access to Bazel cache configured"
        BAZEL_REMOTE_CACHE_ARGUMENT="--remote_cache=grpcs://${BAZEL_CACHE_USER}:${BAZEL_CACHE_PASSWORD}@${BAZEL_CACHE_URL}"
    else
        echo "Read-only access to Bazel cache configured"
        BAZEL_REMOTE_CACHE_ARGUMENT="--remote_cache=grpcs://${BAZEL_CACHE_URL}"
    fi
else
    echo
    echo "BAZEL REMOTE CACHING NOT CONFIGURED!"
    echo "To do so, set BAZEL_CACHE_URL maybe addionally also BAZEL_CACHE_USER and BAZEL_CACHE_PASSWORD to get read-write access"
    echo
    BAZEL_REMOTE_CACHE_ARGUMENT="--remote_cache="""
fi

if [ "${CI}" == "true" ]; then
    BAZEL_CONFIG_ARGS="--config=debug"
    echo "Running on a CI machine, using addional args: \"${BAZEL_CONFIG_ARGS}\""
else
    BAZEL_CONFIG_ARGS=""
    echo "Running on a non CI machine"
fi
echo "========================================================================="

# We encountered false cache hits with remote caching due to environment variables
# not being propagated to external dependeny builds
# In that case `--host_action_env=...` (in addition to `--action_env`) might help
# Currently we don't use any external dependencies though.

# shellcheck disable=SC2086
bazel "${ACTION}" \
    ${BAZEL_CONFIG_ARGS} \
    --execution_log_json_file="${EXECUTION_LOG_FILE_NAME}" \
    --action_env=SYSTEM_DIGEST="$SYSTEM_DIGEST" \
    --action_env=CMK_BASE_BRANCH="master" \
    ${RUSTUP_HOME:+--action_env=RUSTUP_HOME="$RUSTUP_HOME"} \
    --host_action_env=SYSTEM_DIGEST="$SYSTEM_DIGEST" \
    --host_action_env=CMK_BASE_BRANCH="master" \
    ${RUSTUP_HOME:+--host_action_env=RUSTUP_HOME="$RUSTUP_HOME"} \
    "${BAZEL_REMOTE_CACHE_ARGUMENT}" \
    ${BAZEL_EXTRA_ARGS} \
    "${TARGET[@]}"
