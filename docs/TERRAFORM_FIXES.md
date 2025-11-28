# Terraform 오류 해결 가이드

## SSH 키 페어 오류 해결

### 문제
```
Error: Invalid function argument
no file exists at "./keys/id_rsa.pub"
```

### 해결 방법

#### 옵션 1: SSH 키 생성 (권장)

```bash
# SSH 키 생성
mkdir -p terraform/keys
ssh-keygen -t rsa -b 4096 -f terraform/keys/id_rsa -N ""

# Terraform 적용
terraform apply -var="create_s3_bucket=false"
```

#### 옵션 2: 키 없이 배포 (나중에 키 추가)

키가 없으면 EC2 인스턴스는 키 없이 생성됩니다. 이후에:
- AWS 콘솔에서 키 페어 연결
- Session Manager 사용
- 또는 키를 수동으로 추가

## S3 버킷 권한 오류 해결

### 문제
```
Error: User is not authorized to perform: s3:CreateBucket
```

### 해결 방법

#### 옵션 1: S3 버킷 없이 배포 (권장)

```bash
terraform apply -var="create_s3_bucket=false"
```

#### 옵션 2: IAM 역할에 S3 권한 추가

IAM 역할에 다음 권한 추가:
- `AmazonS3FullAccess` 또는
- 필요한 권한만: `s3:CreateBucket`, `s3:PutBucketVersioning`, `s3:PutBucketEncryption` 등

그 후:
```bash
terraform apply -var="create_s3_bucket=true"
```

## 빠른 해결 (권장)

```bash
# SSH 키 생성
mkdir -p terraform/keys
ssh-keygen -t rsa -b 4096 -f terraform/keys/id_rsa -N ""

# S3 버킷 없이 배포
terraform apply -var="create_s3_bucket=false"
```

## 배포 후 SSH 접속

### 방법 1: 생성한 키 사용

```bash
ssh -i terraform/keys/id_rsa ec2-user@<web_server_public_ip>
```

### 방법 2: Session Manager 사용 (키 없이)

AWS Systems Manager Session Manager를 사용하면 키 없이도 접속 가능합니다.

