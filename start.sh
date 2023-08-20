#!/bin/bash
set -euo pipefail
IFS=$'\n\t'

set -o allexport; source .env; set +o allexport

python server.py
