#!/bin/sh
echo "import toptool.fixtures as f;f.showroom_fixture_state_no_confirmation()"|python3 manage.py shell
