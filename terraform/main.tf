# Provider 설정
provider "aws" {
  region = var.aws_region

  default_tags {
    tags = var.tags
  }
}

# SSH 키 공개키 (파일이 있는 경우만)
locals {
  ssh_public_key = fileexists("${path.module}/keys/id_rsa.pub") ? file("${path.module}/keys/id_rsa.pub") : ""
  has_ssh_key    = fileexists("${path.module}/keys/id_rsa.pub")
}

