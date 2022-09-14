#!/usr/bin/env bash

set -e

mkdir -p logs
cd $(dirname "$BASH_SOURCE")
PYTHON_DIST_PATH=../python3

export PATH=../python3/bin:$PATH
export PYTHONPATH=../deps:pylib:.

BIND=$(python -c 'import config; print(f"{config.listen_host}:{config.listen_port}")')
PID=gunicorn.pid

python -m gunicorn run:app --daemon --pid=$PID --bind $BIND --threads=16 -w 1 --log-level debug --error-logfile logs/gunicorn_error.log --access-logfile logs/gunicorn_access.log --limit-request-line 8000 --capture-output
echo "twitter-clone started successfully"