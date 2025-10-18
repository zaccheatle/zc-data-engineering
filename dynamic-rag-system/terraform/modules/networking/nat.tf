resource "aws_eip" "nat_eip" {
  domain = "vpc"

  tags = {
    Name = "${var.project_name}-${var.env}-nat-eip-${var.aws_region}"
  }
}

resource "aws_nat_gateway" "nat_gateway" {
  allocation_id = aws_eip.nat_eip.allocation_id
  subnet_id = aws_subnet.public_1.id

  tags = {
    Name = "${var.project_name}-${var.env}-nat-${var.aws_region}"
  }
}