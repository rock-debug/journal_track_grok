output "vpc_id" {
  description = "ID of the AWS VPC"
  value       = aws_vpc.main.id
}

output "eks_cluster_name" {
  description = "Name of the EKS cluster"
  value       = aws_eks_cluster.main.name
}

output "eks_cluster_endpoint" {
  description = "Endpoint of the EKS cluster"
  value       = aws_eks_cluster.main.endpoint
}

output "rds_endpoint" {
  description = "Database connection endpoint for RDS PostgreSQL"
  value       = aws_db_instance.postgres.endpoint
}
