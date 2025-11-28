# Terraform 빠른 시작 가이드

## AWS 자격 증명 설정

### 1단계: 환경 변수 설정

```bash
export AWS_ACCESS_KEY_ID=your_access_key_id
export AWS_SECRET_ACCESS_KEY=your_secret_access_key
export AWS_DEFAULT_REGION=ap-northeast-2
```

### 2단계: 자격 증명 확인

```bash
aws sts get-caller-identity
```

### 3단계: Terraform 실행

```bash
terraform init
terraform plan
terraform apply
```

## 자격 증명 설정 방법

### 방법 1: 환경 변수 (임시)

```bash
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_DEFAULT_REGION=ap-northeast-2
```

### 방법 2: AWS CLI (권장)

```bash
aws configure
```

### 방법 3: 자격 증명 파일

```bash
mkdir -p ~/.aws
cat > ~/.aws/credentials << EOF
[default]
aws_access_key_id = your_key
aws_secret_access_key = your_secret
EOF

cat > ~/.aws/config << EOF
[default]
region = ap-northeast-2
EOF
```

## 필요한 AWS 권한

- EC2 Full Access
- VPC Full Access
- S3 Full Access (S3 사용 시)

