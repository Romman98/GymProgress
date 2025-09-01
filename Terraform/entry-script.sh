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
docker run -d -p 80:80 --name gymprogress romman1998/gymprogress:latest
