#!/usr/bin/env bash

cd $(dirname "$BASH_SOURCE")

if [ -f gunicorn.pid ]; then
    kill -9 $(cat gunicorn.pid)
    rm gunicorn.pid
    echo "twitter-clone stopped successfully"
    exit 0
fi