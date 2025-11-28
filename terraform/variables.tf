variable "aws_region" {
  description = "AWS 리전"
  type        = string
  default     = "ap-northeast-2"  # 서울 리전
}

variable "project_name" {
  description = "프로젝트 이름"
  type        = string
  default     = "v2r"
}

variable "environment" {
  description = "환경 (dev, test, prod)"
  type        = string
  default     = "test"
}

variable "vpc_cidr" {
  description = "VPC CIDR 블록"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "가용 영역"
  type        = list(string)
  default     = ["ap-northeast-2a", "ap-northeast-2c"]
}

variable "public_subnet_cidrs" {
  description = "퍼블릭 서브넷 CIDR 블록"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "private_subnet_cidrs" {
  description = "프라이빗 서브넷 CIDR 블록"
  type        = list(string)
  default     = ["10.0.10.0/24", "10.0.11.0/24"]
}

variable "instance_type" {
  description = "EC2 인스턴스 타입"
  type        = string
  default     = "t3.medium"
}

variable "instance_ami" {
  description = "EC2 AMI ID (Ubuntu 22.04 LTS 권장)"
  type        = string
  default     = ""  # 리전별로 다름, terraform apply 시 입력 필요
}

variable "allowed_ssh_cidr" {
  description = "SSH 접근 허용 CIDR (주의: 테스트 환경만)"
  type        = string
  default     = "0.0.0.0/0"  # 보안상 실제 IP로 제한 권장
}

variable "create_s3_bucket" {
  description = "S3 버킷 생성 여부 (IAM 역할에 S3 권한이 있는 경우만)"
  type        = bool
  default     = false
}

variable "tags" {
  description = "공통 태그"
  type        = map(string)
  default = {
    Project     = "V2R"
    Environment = "test"
    ManagedBy   = "Terraform"
    Purpose     = "Vulnerability-Testing"
  }
}

