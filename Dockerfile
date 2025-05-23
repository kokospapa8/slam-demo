FROM nvidia/cuda:11.8.0-cudnn8-devel-ubuntu20.04
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y tzdata && \
    ln -fs /usr/share/zoneinfo/Asia/Seoul /etc/localtime && \
    dpkg-reconfigure --frontend noninteractive tzdata

# 필수 패키지 설치
RUN apt-get update && apt-get install -y \
    git cmake build-essential \
    libboost-all-dev libeigen3-dev \
    libflann-dev libfreeimage-dev \
    libgoogle-glog-dev libgflags-dev \
    libglew-dev qtbase5-dev \
    libatlas-base-dev libsuitesparse-dev \
    libsqlite3-dev \
    ffmpeg \
    libceres-dev libcgal-dev libmetis-dev \
    wget unzip

# COLMAP 소스 코드 클론
RUN git clone https://github.com/colmap/colmap.git /opt/colmap

WORKDIR /opt/colmap

ENV TMPDIR=/opt/tmp
RUN mkdir -p /opt/tmp

#RUN mkdir build && cd build && \
#    cmake .. -DCMAKE_BUILD_TYPE=Release && \
#    make -j$(nproc) && make install
RUN mkdir build && cd build && \
    TMPDIR=/opt/tmp cmake .. -DCMAKE_BUILD_TYPE=Release && \
    TMPDIR=/opt/tmp make -j$(nproc) && \
    make install
# 환경 변수 설정
ENV PATH="/usr/local/bin:${PATH}"

RUN apt-get install -y python3-pip
RUN pip3 install open3d numpy matplotlib ffmpeg
RUN mkdir /workspace

COPY . /workspace
WORKDIR /workspace

