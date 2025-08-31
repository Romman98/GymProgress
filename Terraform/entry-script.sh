#!/bin/bash
# Update and install Docker
yum update -y
amazon-linux-extras install docker -y
service docker start
usermod -a -G docker ec2-user

# Pull and run your container
docker pull romman1998/gymprogress:latest
docker run -d -p 80:80 romman1998/gymprogress:latest
