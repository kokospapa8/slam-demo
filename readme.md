


### merge
```
 colmap model_merger --input_path1 sparse/0 --input_path2 sparse/1 --output_path sparse/merged --alignment_type geometry 
```


수동align 방법 - text export 후 직접sudo apt-get update


# image build
sudo apt-get install -y docker.io4
sudo systemctl start docker
sudo systemctl enable docker

# NVIDIA Container Toolkit 설치
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt-get update
sudo apt-get install -y nvidia-docker2
sudo systemctl restart docker 병합 -> 무리데스


docker build -t colmap-cuda .
docker run --gpus all -it --name colmap_dev colmap-cuda /bin/bash
docker run --gpus all -it \
  -v $(pwd)/output:/workspace/output \
  --name colmap_dev \
  colmap-cuda /bin/bash

docker start -ai colmap_dev

$ scp -i ~/.ssh/robosuite.pem visualslam/test1.mp4 ubuntu@16.184.16.175:/home/ubuntu/slam-demo/
docker cp test1.mp4 colmap_dev:/workspace/