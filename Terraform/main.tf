terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
  backend "s3" {
    bucket         = "my-terraform-gymprogress-bucket"  # replace with your S3 bucket name
    key            = "gymprogress/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
  }

}

# Configure the AWS Provider
provider "aws" {
  region = "us-east-1"
}

resource "aws_vpc" "main" {
  cidr_block = "192.168.0.0/16"

  tags = {
    "Name" = "Production Gym Progress"
  }
}

resource "aws_subnet" "web" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "192.168.0.0/16"
  availability_zone = "us-east-1a"
  tags = {
    "Name" = "Gym Progress Subnet"
  }
}

resource "aws_internet_gateway" "my_web_igw" {
  vpc_id = aws_vpc.main.id
  tags = {
    "Name" = "Web IGW"
  }
}


resource "aws_default_route_table" "main_vpc_default_rt" {
  default_route_table_id = aws_vpc.main.default_route_table_id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.my_web_igw.id
  }
  tags = {
    "Name" = "my-default-rt"
  }
}


resource "aws_default_security_group" "default_sec_group" {
  vpc_id = aws_vpc.main.id
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    # cidr_blocks = [var.my_public_ip]
  }
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    # cidr_blocks = [var.my_public_ip]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = {
    "Name" = "Default Security Group"
  }
}

resource "aws_key_pair" "gymprogress_ssh_key" {
  key_name   = "testing_ssh_key"
  public_key = var.ssh_public_key
}
variable "ssh_public_key" {}

# Create a EC2 Instance
resource "aws_instance" "my_vm" {
  ami                         = "ami-0de716d6197524dd9"
  instance_type               = "t3.micro"
  subnet_id                   = aws_subnet.web.id
  vpc_security_group_ids      = [aws_default_security_group.default_sec_group.id]
  associate_public_ip_address = true
  key_name                    = aws_key_pair.gymprogress_ssh_key.key_name
  user_data                   = file("entry-script.sh")

  tags = {
    "Name" = "My EC2 Instance - Amazon Linux 3"
  }
}
