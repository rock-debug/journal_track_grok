provider "aws" {
  region = var.aws_region
}

# Generate a new SSH key pair
resource "tls_private_key" "rsa" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

resource "aws_key_pair" "key_pair" {
  key_name   = "journal-tracker-key"
  public_key = tls_private_key.rsa.public_key_openssh
}

# Save the private key locally so you can SSH in
resource "local_file" "private_key" {
  content         = tls_private_key.rsa.private_key_pem
  filename        = "${path.module}/journal-tracker-key.pem"
  file_permission = "0400"
}

# Get latest Ubuntu 22.04 AMI
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }
}

# Use the Default VPC for simplicity
data "aws_vpc" "default" {
  default = true
}

# Security Group to allow necessary ports
resource "aws_security_group" "app_sg" {
  name        = "journal-tracker-sg"
  description = "Allow App, SSH, Grafana, Prometheus, Jenkins, and K3s"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "Flask App"
    from_port   = 5000
    to_port     = 5000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "Grafana"
    from_port   = 3000
    to_port     = 3000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "Prometheus"
    from_port   = 9090
    to_port     = 9090
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  ingress {
    description = "Jenkins"
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  ingress {
    description = "K3s Kubernetes API"
    from_port   = 6443
    to_port     = 6443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# EC2 Instance (Free Tier Eligible)
resource "aws_instance" "app_server" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = "m7i-flex.large" # Free Tier eligible
  key_name      = aws_key_pair.key_pair.key_name
  vpc_security_group_ids = [aws_security_group.app_sg.id]

  # Allocate 20GB of storage (Free tier allows up to 30GB)
  root_block_device {
    volume_size = 20 
    volume_type = "gp3"
  }

  tags = {
    Name = "Journal-Tracker-Server"
  }
}
