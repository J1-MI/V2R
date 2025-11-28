# 증거 저장소 S3 버킷 (선택적 - IAM 역할에 S3 권한이 있는 경우만)
# IAM 역할에 S3 권한이 없으면 이 리소스를 주석 처리하세요
resource "aws_s3_bucket" "evidence" {
  count = var.create_s3_bucket ? 1 : 0
  bucket = "${var.project_name}-${var.environment}-evidence-${data.aws_caller_identity.current.account_id}"

  tags = merge(
    var.tags,
    {
      Name        = "${var.project_name}-${var.environment}-evidence"
      Purpose     = "Proof-of-Concept-Evidence-Storage"
    }
  )
}

# 버전 관리 활성화
resource "aws_s3_bucket_versioning" "evidence" {
  count  = var.create_s3_bucket ? 1 : 0
  bucket = aws_s3_bucket.evidence[0].id

  versioning_configuration {
    status = "Enabled"
  }
}

# 암호화 활성화
resource "aws_s3_bucket_server_side_encryption_configuration" "evidence" {
  count  = var.create_s3_bucket ? 1 : 0
  bucket = aws_s3_bucket.evidence[0].id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# 퍼블릭 액세스 차단
resource "aws_s3_bucket_public_access_block" "evidence" {
  count  = var.create_s3_bucket ? 1 : 0
  bucket = aws_s3_bucket.evidence[0].id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# 수명 주기 정책 (30일 후 자동 삭제 옵션)
resource "aws_s3_bucket_lifecycle_configuration" "evidence" {
  bucket = aws_s3_bucket.evidence.id

  rule {
    id     = "delete-old-evidence"
    status = "Enabled"

    filter {
      prefix = ""
    }

    expiration {
      days = 30  # 테스트 후 조정 가능
    }

    abort_incomplete_multipart_upload {
      days_after_initiation = 7
    }
  }
}

# 현재 AWS 계정 ID 조회
data "aws_caller_identity" "current" {}

