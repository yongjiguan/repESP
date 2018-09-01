SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
MYPY_SNAPSHOT="$SCRIPT_DIR/mypy_snapshot.out"

run_mypy() {
    pushd "$SCRIPT_DIR"/.. > /dev/null
    mypy repESP/*.py
    popd > /dev/null
}

run_tests() {
    nosetests3 -s "$SCRIPT_DIR"/.. 2>&1
}
