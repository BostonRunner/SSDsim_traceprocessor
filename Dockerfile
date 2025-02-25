FROM ubuntu:22.04
LABEL maintainer = "wuruofei2022@mail.nwpu.edu.cn"

RUN apt-get update
RUN apt-get install fio -y


