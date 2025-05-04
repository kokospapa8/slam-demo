FROM nvidia/cuda:11.8.0-cudnn8-devel-ubuntu20.04

# 필수 패키지 설치
RUN apt-get update && apt-get install -y \
    tzdata \
    git cmake build-essential \
    libboost-all-dev libeigen3-dev \
    libflann-dev libfreeimage-dev \
    libgoogle-glog-dev libgflags-dev \
    libglew-dev qtbase5-dev \
    libatlas-base-dev libsuitesparse-dev \
    wget unzip

# COLMAP 소스 코드 클론
RUN git clone https://github.com/colmap/colmap.git /opt/colmap

# COLMAP 빌드
WORKDIR /opt/colmap
RUN mkdir build && cd build && \
    cmake .. -DCMAKE_BUILD_TYPE=Release && \
    make -j$(nproc) && make install

# 환경 변수 설정
ENV PATH="/usr/local/bin:${PATH}"