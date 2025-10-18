resource "aws_security_group" "lambda_sg" {
  name = "${var.project_name}-${var.env}-lambda-sg-${var.aws_region}"
  description = "Security group for all project lambda functions"
  vpc_id = aws_vpc.vpc.id

  tags = {
    Name = "${var.project_name}-${var.env}-lambda-sg-${var.aws_region}"
  }
}

resource "aws_security_group" "database_sg" {
  name = "${var.project_name}-${var.env}-database-sg-${var.aws_region}"
  description = "Security group for aurora postgres rds instance"
  vpc_id = aws_vpc.vpc.id

  tags = {
    Name = "${var.project_name}-${var.env}-database-sg-${var.aws_region}"
  }
}

resource "aws_vpc_security_group_egress_rule" "lambda_tcp_egress_rule" {
  security_group_id = aws_security_group.lambda_sg.id
  cidr_ipv4 = "0.0.0.0/0"
  from_port = 443
  ip_protocol = "tcp"
  to_port = 443

  tags = {
    Name = "${var.project_name}-${var.env}-lambda-tcp-egress-${var.aws_region}"
  }
}

resource "aws_vpc_security_group_egress_rule" "lambda_db_egress_rule" {
  security_group_id = aws_security_group.lambda_sg.id
  referenced_security_group_id = aws_security_group.database_sg.id
  from_port = 5432
  ip_protocol = "tcp"
  to_port = 5432

  tags = {
    Name = "${var.project_name}-${var.env}-lambda-db-egress-${var.aws_region}"
  }
}


resource "aws_vpc_security_group_ingress_rule" "db_ingress_rule" {
  security_group_id = aws_security_group.database_sg.id
  referenced_security_group_id = aws_security_group.lambda_sg.id
  from_port = 5432
  ip_protocol = "tcp"
  to_port = 5432

  tags = {
    Name = "${var.project_name}-${var.env}-db-lambda-ingress-${var.aws_region}"
  }
}