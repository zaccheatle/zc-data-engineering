data "aws_availability_zones" "available" {
  state = "available"
}

resource "aws_subnet" "public_1" {
  vpc_id = aws_vpc.vpc.id
  cidr_block        = "10.0.1.0/24"
  availability_zone = data.aws_availability_zones.available.names[0]
  map_public_ip_on_launch = true

  tags = {
    Name = "${var.project_name}-${var.env}-public-subnet-1-${var.aws_region}"
  }
}

resource "aws_subnet" "public_2" {
  vpc_id = aws_vpc.vpc.id
  cidr_block        = "10.0.2.0/24"
  availability_zone = data.aws_availability_zones.available.names[1]
  map_public_ip_on_launch = true

  tags = {
    Name = "${var.project_name}-${var.env}-public-subnet-2-${var.aws_region}"
  }
}

resource "aws_subnet" "private-db-subnet-1" {
  vpc_id = aws_vpc.vpc.id
  cidr_block        = "10.0.11.0/24"
  availability_zone = data.aws_availability_zones.available.names[0]

  tags = {
    Name = "${var.project_name}-${var.env}-private-db-subnet-1-${var.aws_region}"
  }
}

resource "aws_subnet" "private-db-subnet-2" {
  vpc_id = aws_vpc.vpc.id
  cidr_block        = "10.0.12.0/24"
  availability_zone = data.aws_availability_zones.available.names[1]

  tags = {
    Name = "${var.project_name}-${var.env}-private-db-subnet-2-${var.aws_region}"
  }
}

resource "aws_subnet" "private-lambda-subnet-1" {
  vpc_id = aws_vpc.vpc.id
  cidr_block        = "10.0.21.0/24"
  availability_zone = data.aws_availability_zones.available.names[0]

  tags = {
    Name = "${var.project_name}-${var.env}-private-lambda-subnet-1-${var.aws_region}"
  }
}

resource "aws_subnet" "private-lambda-subnet-2" {
  vpc_id = aws_vpc.vpc.id
  cidr_block        = "10.0.22.0/24"
  availability_zone = data.aws_availability_zones.available.names[1]

  tags = {
    Name = "${var.project_name}-${var.env}-private-lambda-subnet-2-${var.aws_region}"
  }
}