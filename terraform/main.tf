# Provider 설정
provider "aws" {
  region = var.aws_region

  default_tags {
    tags = var.tags
  }
}

