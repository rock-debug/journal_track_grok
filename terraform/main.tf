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
    description = "HTTP Traffic (K3s LoadBalancer)"
    from_port   = 80
    to_port     = 80
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

resource "aws_instance" "app_server" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = "m7i-flex.large" 
  key_name      = aws_key_pair.key_pair.key_name
  vpc_security_group_ids = [aws_security_group.app_sg.id]


  root_block_device {
    volume_size = 20 
    volume_type = "gp3"
  }
  user_data = <<-EOF
    #!/bin/bash
    set -e
    exec > /var/log/bootstrap.log 2>&1

    echo "=== [1/6] Updating system packages ==="
    apt-get update -y
    apt-get install -y curl wget git unzip gnupg lsb-release ca-certificates software-properties-common

    echo "=== [2/6] Installing Docker ==="
    install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    chmod a+r /etc/apt/keyrings/docker.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
    apt-get update -y
    apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    usermod -aG docker ubuntu
    systemctl enable docker
    systemctl start docker

    echo "=== [3/6] Installing Docker Compose (standalone) ==="
    curl -SL https://github.com/docker/compose/releases/download/v2.27.0/docker-compose-linux-x86_64 -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose

    echo "=== [4/6] Installing kubectl ==="
    curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
    install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
    rm -f kubectl

    echo "=== [5/6] Installing K3s (lightweight Kubernetes) ==="
    curl -sfL https://get.k3s.io | sh -
    systemctl enable k3s
    mkdir -p /home/ubuntu/.kube
    cp /etc/rancher/k3s/k3s.yaml /home/ubuntu/.kube/config
    chown ubuntu:ubuntu /home/ubuntu/.kube/config
    chmod 600 /home/ubuntu/.kube/config
    sed -i 's/127.0.0.1/localhost/g' /home/ubuntu/.kube/config

    echo "=== [6/6] Installing Jenkins ==="
    wget -O /usr/share/keyrings/jenkins-keyring.asc https://pkg.jenkins.io/debian-stable/jenkins.io-2026.key
    echo "deb [signed-by=/usr/share/keyrings/jenkins-keyring.asc] https://pkg.jenkins.io/debian-stable binary/" | tee /etc/apt/sources.list.d/jenkins.list > /dev/null
    apt-get update -y
    apt-get install -y openjdk-21-jre jenkins
    usermod -aG docker jenkins
    systemctl enable jenkins
    systemctl start jenkins

    echo "=== Bootstrap complete! All tools installed. ==="
  EOF

  tags = {
    Name = "Journal-Tracker-Server"
  }
}
