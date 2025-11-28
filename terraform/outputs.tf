output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.main.id
}

output "public_subnet_ids" {
  description = "퍼블릭 서브넷 ID 목록"
  value       = aws_subnet.public[*].id
}

output "private_subnet_ids" {
  description = "프라이빗 서브넷 ID 목록"
  value       = aws_subnet.private[*].id
}

output "web_server_instance_id" {
  description = "웹 서버 EC2 인스턴스 ID"
  value       = aws_instance.web_server.id
}

output "web_server_public_ip" {
  description = "웹 서버 퍼블릭 IP"
  value       = aws_instance.web_server.public_ip
}

output "scanner_instance_id" {
  description = "스캐너 EC2 인스턴스 ID"
  value       = aws_instance.scanner.id
}

output "scanner_public_ip" {
  description = "스캐너 퍼블릭 IP"
  value       = aws_instance.scanner.public_ip
}

output "s3_evidence_bucket" {
  description = "증거 저장소 S3 버킷 이름"
  value       = var.create_s3_bucket ? (length(aws_s3_bucket.evidence) > 0 ? aws_s3_bucket.evidence[0].id : null) : null
}

output "security_group_web_id" {
  description = "웹 서버 보안 그룹 ID"
  value       = aws_security_group.web_server.id
}

output "security_group_scanner_id" {
  description = "스캐너 보안 그룹 ID"
  value       = aws_security_group.scanner.id
}

