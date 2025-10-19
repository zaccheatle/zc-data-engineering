resource "aws_db_subnet_group" "database" {
  name       = "${var.project_name}-${var.env}-db-subnet-group"
  subnet_ids = var.private_subnet_ids

  tags = {
    Name = "${var.project_name}-${var.env}-db-subnet-group-${var.aws_region}"
  }
}

resource "random_password" "db_password" {
  length  = 32
  special = true
}

resource "aws_rds_cluster" "database" {
  cluster_identifier      = "${var.project_name}-${var.env}-cluster"
  engine                  = "aurora-postgresql"
  engine_mode             = "provisioned"
  engine_version          = "15.3"
  database_name           = var.project_name
  master_username         = "admin"
  master_password         = random_password.db_password.result

  db_subnet_group_name    = aws_db_subnet_group.database.name
  vpc_security_group_ids  = [var.database_security_group]

  storage_encrypted       = true
  kms_key_id             = var.database_kms_key

  backup_retention_period = 7
  preferred_backup_window = "03:00-04:00"
  preferred_maintenance_window = "sun:04:00-sun:05:00"

  skip_final_snapshot     = true

  serverlessv2_scaling_configuration {  # Add this!
    min_capacity = 0.5
    max_capacity = 2.0
  }

  tags = {
    Name = "${var.project_name}-${var.env}-db-cluster-${var.aws_region}"
  }
}

resource "aws_secretsmanager_secret_version" "db_credentials" {
  secret_id = var.database_secret_arn
  secret_string = jsonencode({
    username = aws_rds_cluster.database.master_username
    password = random_password.db_password.result
    host     = aws_rds_cluster.database.endpoint
    port     = aws_rds_cluster.database.port
    dbname   = aws_rds_cluster.database.database_name
  })
}

resource "aws_rds_cluster_instance" "database_instance" {
  count              = 1 # for dev env/poc only
  identifier         = "${var.project_name}-${var.env}-instance-${count.index}"
  cluster_identifier = aws_rds_cluster.database.id
  instance_class     = "db.serverless"  # For Serverless v2
  engine             = aws_rds_cluster.database.engine
  engine_version     = aws_rds_cluster.database.engine_version

  tags = {
    Name = "${var.project_name}-${var.env}-db-instance-${count.index}-${var.aws_region}"
  }
}