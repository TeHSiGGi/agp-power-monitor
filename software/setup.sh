#!/bin/bash
# AGP Power Monitor
# Copyright (C) 2025 - tehsiggi

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

set -e

VENV_DIR=".venv"

install() {
    python3 -m venv "$VENV_DIR"
    . "$VENV_DIR/bin/activate"
    pip install --upgrade pip
    if [ -f requirements.txt ]; then
        pip install -r requirements.txt
    fi
    echo "Installation complete."
}

activate_venv() {
    if [ -d "$VENV_DIR" ]; then
        echo "Run: . $VENV_DIR/bin/activate"
    else
        echo "Virtual environment not found. Run './setup.sh install' first."
        exit 1
    fi
}

start() {
    if [ -d "$VENV_DIR" ]; then
        . "$VENV_DIR/bin/activate"
        if [ -f src/main.py ]; then
            python src/main.py "$@"
            echo $@
        else
            echo "main.py not found."
            exit 1
        fi
    else
        echo "Virtual environment not found. Run './setup.sh install' first."
        exit 1
    fi
}

case "$1" in
    install)
        install
        ;;
    activate-venv)
        activate_venv
        ;;
    start)
        shift
        start "$@"
        ;;
    *)
        echo "Usage: $0 {install|activate-venv|start}"
        exit 1
        ;;
esac