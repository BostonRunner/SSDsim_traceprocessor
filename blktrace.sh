cd ./results
blktrace -d /dev/sda1 -w 600 -o - | blkparse -i - >> result.log &
