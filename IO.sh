#!/bin/bash
set -e

# 镜像定义
IMAGES=(
  "ubuntu:22.04"
  "opensuse/leap:15.5"
  "parrotsec/security"
  "debian:11"
  "alpine:3.18"
  "archlinux:latest"
)

CONTAINER_PREFIX="docker_blktest"
NUM_CONTAINERS=${#IMAGES[@]}
WRITE_ROUNDS=5
FILES_PER_ROUND=3
BLOCK_SIZE="4K"
TOTAL_SIZE="256K"
TEST_DIR="/mnt/testdir"

# 安装 fio
install_fio() {
  local container=$1
  local image=$2

  if [[ "$image" == ubuntu* || "$image" == debian* || "$image" == parrotsec* ]]; then
    docker exec "$container" bash -c "apt-get update && apt-get install -y fio"
  elif [[ "$image" == alpine* ]]; then
    docker exec "$container" sh -c "apk update && apk add fio"
  elif [[ "$image" == archlinux* ]]; then
    docker exec "$container" bash -c "pacman -Syu --noconfirm fio"
  elif [[ "$image" == opensuse* ]]; then
    docker exec "$container" bash -c "zypper --non-interactive install fio"
  else
    echo "[ERROR] 不支持的镜像类型: $image"
  fi
}

# 启动并准备容器（镜像拉取 + 启动 + fio 安装 + 文件准备）
prepare_container() {
  local idx=$1
  local IMAGE=${IMAGES[$idx]}
  local CONTAINER_NAME="${CONTAINER_PREFIX}$((idx+1))"

  echo "[INFO] [$CONTAINER_NAME] 开始拉取镜像 $IMAGE"

  PULL_OK=0
  for attempt in {1..3}; do
    if docker pull "$IMAGE"; then
      PULL_OK=1
      echo "[INFO] [$CONTAINER_NAME] 镜像拉取成功"
      break
    else
      echo "[WARN] [$CONTAINER_NAME] 镜像拉取失败，重试中（$attempt/3）..."
      sleep 3
    fi
  done

  if [[ $PULL_OK -ne 1 ]]; then
    echo "[ERROR] [$CONTAINER_NAME] 镜像拉取连续失败，跳过"
    exit 1
  fi

  # 启动容器
  if [[ "$IMAGE" == alpine* ]]; then
    docker run -dit --name "$CONTAINER_NAME" "$IMAGE" sh
  else
    docker run -dit --name "$CONTAINER_NAME" "$IMAGE" bash || docker exec "$CONTAINER_NAME" sh
  fi

  echo "[INFO] [$CONTAINER_NAME] 安装 fio 中..."
  install_fio "$CONTAINER_NAME" "$IMAGE"

  # 创建测试目录 + 预分配文件
  docker exec "$CONTAINER_NAME" sh -c "mkdir -p $TEST_DIR"
  for j in $(seq 1 10); do
    docker exec "$CONTAINER_NAME" sh -c "dd if=/dev/zero of=$TEST_DIR/file$j bs=1M count=1 status=none || true"
  done

  echo "[INFO] [$CONTAINER_NAME] 初始化完成"
}

# 容器执行随机写操作
perform_io() {
  local idx=$1
  local CONTAINER_NAME="${CONTAINER_PREFIX}$((idx+1))"

  for ((round=1; round<=WRITE_ROUNDS; round++)); do
    for j in $(seq 1 $FILES_PER_ROUND); do
      FILENAME="$TEST_DIR/file$(( (round-1)*FILES_PER_ROUND + j ))"
      docker exec "$CONTAINER_NAME" sh -c "fio --name=write_${round}_$j --filename=$FILENAME --rw=randwrite --bs=$BLOCK_SIZE --size=$TOTAL_SIZE --ioengine=sync --numjobs=1 --loops=1 --direct=1 || true"
    done
  done
}

# === 第一组容器 ===
echo "[STAGE 1] 启动前 3 个容器..."
for i in 0 1 2; do
  (prepare_container $i; perform_io $i) &
done

sleep 15
echo "[STAGE 2] 启动后 3 个容器..."

# === 第二组容器 ===
for i in 3 4 5; do
  (prepare_container $i; perform_io $i) &
done

wait

# 停止所有容器
for ((i=0; i<NUM_CONTAINERS; i++)); do
  docker stop "${CONTAINER_PREFIX}$((i+1))" > /dev/null || true
done

echo "[INFO] 所有容器写入并关闭完成"
