terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.16"
    }
  }

  required_version = ">= 1.2.0"
}

resource "aws_vpc" "Main" { # Creating VPC here
  cidr_block       = var.main_vpc_cidr
  instance_tenancy = "default"
}

resource "aws_internet_gateway" "IGW" { # Creating Internet Gateway
  vpc_id = aws_vpc.Main.id              # vpc_id will be generated after we create VPC
}

resource "aws_subnet" "publicsubnets" { # Creating Public Subnet
  vpc_id     = aws_vpc.Main.id
  cidr_block = var.public_subnets
}

resource "aws_route_table" "PublicRT" { # Creating RT for Public Subnet
  vpc_id = aws_vpc.Main.id
  route {
    cidr_block = "0.0.0.0/0" # Traffic from Public Subnet reaches Internet via Internet Gateway
    gateway_id = aws_internet_gateway.IGW.id
  }
}

resource "aws_route_table_association" "PublicRTassociation" { # Route table Association with Public Subnet
  subnet_id      = aws_subnet.publicsubnets.id
  route_table_id = aws_route_table.PublicRT.id
}

resource "aws_default_network_acl" "default" {
  default_network_acl_id = aws_vpc.Main.default_network_acl_id

  ingress {
    protocol   = -1
    rule_no    = 100
    action     = "allow"
    cidr_block = "0.0.0.0/0"
    from_port  = 0
    to_port    = 0
  }

  egress {
    protocol   = -1
    rule_no    = 100
    action     = "allow"
    cidr_block = "0.0.0.0/0"
    from_port  = 0
    to_port    = 0
  }
}

resource "aws_default_security_group" "default" {
  vpc_id = aws_vpc.Main.id

  ingress {
    protocol    = "tcp"
    from_port   = 22 #SSH
    to_port     = 22
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    protocol    = "tcp"
    from_port   = 80 #HTTP
    to_port     = 80
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    protocol    = "tcp"
    from_port   = 443 #HTTPS
    to_port     = 443
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}


resource "aws_instance" "BPweb_server" {
  ami           = "ami-0f540e9f488cfa27d"
  instance_type = "t2.micro"
  key_name      = var.keyname
  subnet_id     = aws_subnet.publicsubnets.id

  tags = {
    Name = "BPForwarder"
  }
}

resource "aws_eip" "BPWebserverEIP" { #Create Elastic IP address
  instance = aws_instance.BPweb_server.id
  vpc      = true
}
