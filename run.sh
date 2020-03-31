#!/usr/bin/env bash

python --version >/dev/null 2>&1 || { echo >&2 "I require python@3 utility but it's not installed. ¯\_(ツ)_/¯ Aborting."; exit 1; }
pip --version >/dev/null 2>&1 || { echo >&2 "I require pip utility but it's not installed. ¯\_(ツ)_/¯ Aborting."; exit 1; }

clear

pip install -r requirements.txt
python vgchartz-full-crawler.py
