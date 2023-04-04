#!/bin/bash

pip3 install -r requirements.txt

chmod +x "$PWD/src/main.py"
python_path=$(which python)

$python_path "src/main.py" $1 $2 >logs.log 2>&1
