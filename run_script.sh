#!/bin/bash

pip3 install -r requirements.txt

chmod +x "$PWD/src/main.py"
python_path=$(which python)

(crontab -l ; echo "0 */6 * * * $python_path $PWD/src/main.py $1 $2 >/tmp/mycommand.log 2>&1") | crontab -
