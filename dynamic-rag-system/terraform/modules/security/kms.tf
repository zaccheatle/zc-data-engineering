resource "aws_kms_key" "db_key" {
  description = "KMS key for aurora postgres database"
  enable_key_rotation = true

  tags = {
    Name = "${var.project_name}-${var.env}-db-kms-key-${var.aws_region}"
  }
}

resource "aws_kms_alias" "db_kms_alias"{
  name = "alias/${var.project_name}-${var.env}-database"
  target_key_id = aws_kms_key.db_key.id
}

resource "aws_kms_key" "application" {
  description = "KMS key for general application use"
  enable_key_rotation = true

  tags = {
    Name = "${var.project_name}-${var.env}-application-kms-key-${var.aws_region}"
  }
}

resource "aws_kms_alias" "general_kms_alias"{
  name = "alias/${var.project_name}-${var.env}-application"
  target_key_id = aws_kms_key.application.id
}