#!/bin/bash
# Update packages
sudo dnf update -y

# Install Docker
sudo dnf install -y docker

# Start Docker and enable at boot
sudo systemctl start docker
sudo systemctl enable docker

# Add ec2-user to Docker group
sudo usermod -aG docker ec2-user

# Pull and run your container
docker pull romman1998/gymprogress:latest
cat <<EOF >> /home/ec2-user/deploy.sh
#!/bin/bash

CONTAINERS=$(docker ps -aq)
IMAGE_NAME="romman1998/gymprogress"
TAG="latest"
PORT=80

runContainer() {
        docker run -d -p $PORT:80 --name gymprocess \
                $IMAGE_NAME:$TAG
}

if [[ -n "$CONTAINERS" ]];then
        docker stop "$CONTAINERS"
        docker rm "$CONTAINERS"
        runContainer

else
        runContainer
fi 
EOF

chmod +x /home/ec2-user/deploy.sh
/home/ec2-user/deploy.sh

