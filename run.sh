#!/bin/bash

mkdir results
cd ./results || exit
echo "directory created"
touch result.txt
touch result.log
echo "result.txt result.log created"
echo "blktrace activating"
cd ..
docker system prune -af --volumes

./blktrace.sh
./IO.sh


cd ./results || exit
grep 'A' result.log | grep " W " > result_temp.txt
sort -n -k 4 result_temp.txt > result.txt
cd ..

echo "processing I/O trace..." & sleep 60

python3 main.py
python3 trans.py
echo "program finished"
