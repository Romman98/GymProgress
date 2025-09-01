#!/bin/bash
# Update packages
sudo dnf update -y
echo "done" > log.txt
# Install Docker
sudo dnf install -y docker
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker ec2-user
echo "done" >> log.txt
# Format the volume if not already
sudo mkfs -t ext4 /dev/nvme1n1 || true

# Create mount point
sudo mkdir -p /mnt/gymprogress_data

# Mount volume
sudo mount /dev/nvme1n1 /mnt/gymprogress_data

# Add to fstab to mount on reboot
echo '/dev/nvme1n1 /mnt/gymprogress_data ext4 defaults,nofail 0 2' | sudo tee -a /etc/fstab
echo "done" >> log.txt

# Ensure docker data directory exists on volume
sudo mkdir -p /mnt/gymprogress_data/docker
sudo chown -R ec2-user:ec2-user /mnt/gymprogress_data/docker
echo "done" >> log.txt


# Pull and run your container
docker pull romman1998/gymprogress:latest
cat << 'EOF' > /home/ec2-user/deploy.sh
#!/bin/bash

CONTAINERS=$(docker ps -aq)
IMAGE_NAME="romman1998/gymprogress"
TAG="latest"
PORT=80

runContainer() {
        docker run -d -p $PORT:80 --name gymprocess -v /mnt/gymprogress_data/docker:/app/instance $IMAGE_NAME:$TAG
}

docker pull "$IMAGE_NAME":"$TAG"

if [[ -n "$CONTAINERS" ]];then
        docker stop "$CONTAINERS"
        docker rm "$CONTAINERS"
        runContainer
        echo "done2" >> log.txt
else
        runContainer
        echo "done3" >> log.txt

fi
EOF

chmod +x /home/ec2-user/deploy.sh
/home/ec2-user/deploy.sh

