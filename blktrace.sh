cd ./results
blktrace -d /dev/sda1 -w 210 -o - | blkparse -i - >> result.log &
