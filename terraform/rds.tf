resource "aws_db_subnet_group" "main" {
  name       = "research-tracker-db-subnet-group"
  subnet_ids = [aws_subnet.private_1.id, aws_subnet.private_2.id]

  tags = {
    Name = "research-tracker-db-subnet-group"
  }
}

resource "aws_db_instance" "postgres" {
  identifier             = "research-tracker-db"
  allocated_storage      = 20
  max_allocated_storage  = 100
  engine                 = "postgres"
  engine_version         = "16.3"
  instance_class         = "db.t4g.micro"
  db_name                = var.db_name
  username               = var.db_username
  password               = var.db_password
  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.rds.id]
  skip_final_snapshot    = true
  publicly_accessible    = false

  tags = {
    Name        = "research-tracker-rds"
    Environment = var.environment
  }
}
