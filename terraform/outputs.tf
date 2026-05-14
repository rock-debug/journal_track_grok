output "instance_public_ip" {
  description = "Public IP of the EC2 instance"
  value       = aws_instance.app_server.public_ip
}

output "ssh_command" {
  description = "Command to SSH into the instance"
  value       = "ssh -i journal-tracker-key.pem ubuntu@${aws_instance.app_server.public_ip}"
}

output "flask_app_url" {
  description = "URL to access the Flask Application"
  value       = "http://${aws_instance.app_server.public_ip}:5000"
}

output "grafana_url" {
  description = "URL to access Grafana"
  value       = "http://${aws_instance.app_server.public_ip}:3000"
}

output "jenkins_url" {
  description = "URL to access Jenkins"
  value       = "http://${aws_instance.app_server.public_ip}:8080"
}
