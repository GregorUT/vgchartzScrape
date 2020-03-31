#!/usr/bin/env bash

python --version >/dev/null 2>&1 || { echo >&2 "I require python@3 utility but it's not installed. ¯\_(ツ)_/¯ Aborting."; exit 1; }
pip --version >/dev/null 2>&1 || { echo >&2 "I require pip utility but it's not installed. ¯\_(ツ)_/¯ Aborting."; exit 1; }

clear

echo "\nInstalling deps... "
pip install -r requirements.txt

echo "\nStart crawling... (remember a crawler is the friend nobody likes)"
python vgchartz-full-crawler.py

