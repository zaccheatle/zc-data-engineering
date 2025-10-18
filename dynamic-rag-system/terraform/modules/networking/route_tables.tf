resource "aws_route_table" "public" {
  vpc_id = aws_vpc.vpc.id

  tags = {
    Name = "${var.project_name}-${var.env}-public-route-table-${var.aws_region}"
  }
}

resource "aws_route" "public_internet" {
  route_table_id = aws_route_table.public.id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id = aws_internet_gateway.igw.id
}

resource "aws_route_table_association" "public_1" {
  subnet_id      = aws_subnet.public_1.id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table_association" "public_2" {
  subnet_id      = aws_subnet.public_2.id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table" "private" {
  vpc_id = aws_vpc.vpc.id

  tags = {
    Name = "${var.project_name}-${var.env}-private-route-table-${var.aws_region}"
  }
}

resource "aws_route" "private_internet" {
  route_table_id = aws_route_table.private.id
  destination_cidr_block = "0.0.0.0/0"
  nat_gateway_id = aws_nat_gateway.nat_gateway.id
}

resource "aws_route_table_association" "private_db_1" {
  subnet_id      = aws_subnet.private-db-subnet-1.id
  route_table_id = aws_route_table.private.id
}

resource "aws_route_table_association" "private_db_2" {
  subnet_id      = aws_subnet.private-db-subnet-2.id
  route_table_id = aws_route_table.private.id
}
resource "aws_route_table_association" "private_lambda_1" {
  subnet_id      = aws_subnet.private-lambda-subnet-1.id
  route_table_id = aws_route_table.private.id
}

resource "aws_route_table_association" "private_lambda_2" {
  subnet_id      = aws_subnet.private-lambda-subnet-2.id
  route_table_id = aws_route_table.private.id
}