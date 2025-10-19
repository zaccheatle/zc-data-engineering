resource "aws_secretsmanager_secret" "database_secret" {
  name = "${var.project_name}/${var.env}/database/master"
  description = "Secret for aurora postgres database"
  kms_key_id = aws_kms_key.db_key.id

  tags = {
    Name = "${var.project_name}-${var.env}-db-ssm-${var.aws_region}"
  }
}

resource "aws_secretsmanager_secret" "api_keys" {
  name        = "${var.project_name}/${var.env}/api/keys"
  description = "Secret for api"
  kms_key_id  = aws_kms_key.application.id

  tags = {
    Name = "${var.project_name}-${var.env}-api-ssm-${var.aws_region}"
  }
}