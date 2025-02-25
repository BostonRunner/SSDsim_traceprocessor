# blkparse -i trace -o result.log

# blktrace -d /dev/sda1 -w 30 | blkparse -i - | tee -a result.log

# you can change the name according to your docker system
# docker system prune -af

IMAGE_NAME="blktest"
CONTAINER_NAME="docker_blktest"

echo "building docker image..."
docker build -t $IMAGE_NAME .

# if [ "$(docker ps -q -f name=$CONTAINER_NAME)" ]; then
    # echo "the container $CONTAINER_NAME has already been running, please stop and remove it..."
    # exit
    # docker stop $CONTAINER_NAME
    # docker rm $CONTAINER_NAME
# fi

echo "activating docker container..."
docker run -d --name $CONTAINER_NAME $IMAGE_NAME tail -f /dev/null
echo "container has been activated: $CONTAINER_NAME"
sleep 3
docker exec $CONTAINER_NAME bash -c "fio --name=write_test --rw=write --bs=1M --size=100M --numjobs=1 --directory=/ --group_reporting --ioengine=sync"
sleep 3

CONTAINER_ID=`docker ps -aqf "name=$CONTAINER_NAME"`
# docker commit $CONTAINER_ID nnzhaocs/myubuntu
docker stop $CONTAINER_NAME

