output "vpc_id" {
  description = "vpc id"
  value = aws_vpc.vpc.id
}

output "public_subnet_ids" {
  description = "list of all public subnet ids"
  value = [aws_subnet.public_1.id, aws_subnet.public_2.id]
}

output "private_subnet_ids" {
  description = "list of all private subnet ids"
  value = [aws_subnet.private-lambda-subnet-1.id, aws_subnet.private-lambda-subnet-2.id, aws_subnet.private-db-subnet-1.id, aws_subnet.private-db-subnet-2.id]
}

output "lambda_security_group_id" {
  description = "lambda security group id"
  value = aws_security_group.lambda_sg.id
}

output "database_security_group_id" {
  description = "database security group"
  value = aws_security_group.database_sg.id
}