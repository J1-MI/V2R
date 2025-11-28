# Terraform AMI 조회 오류 해결

## 문제

```
Error: Your query returned no results. Please change your search criteria and try again.
with data.aws_ami.ubuntu
```

## 해결 방법

### 방법 1: AMI 필터 수정 (이미 적용됨)

AMI 필터를 더 넓게 변경했습니다:
- 이전: `ubuntu/images/hub-ssd/ubuntu-jammy-22.04-amd64-server-*`
- 현재: `ubuntu/images/*/ubuntu-jammy-22.04-amd64-server-*`

### 방법 2: 특정 AMI ID 사용

특정 AMI ID를 알고 있다면 변수로 직접 지정:

```bash
terraform apply -var="instance_ami=ami-xxxxxxxxxxxxx"
```

### 방법 3: 수동으로 AMI ID 확인

```bash
# AWS CLI로 AMI 조회
aws ec2 describe-images \
  --owners 099720109477 \
  --filters "Name=name,Values=ubuntu/images/*/ubuntu-jammy-22.04-amd64-server-*" \
            "Name=virtualization-type,Values=hvm" \
            "Name=architecture,Values=x86_64" \
  --query 'Images | sort_by(@, &CreationDate) | [-1].[ImageId,Name]' \
  --output table
```

### 방법 4: terraform.tfvars 파일 생성

```bash
cd terraform
cat > terraform.tfvars << EOF
instance_ami = "ami-0c55b159cbfafe1f0"  # ap-northeast-2 Ubuntu 22.04 LTS
EOF
```

## 리전별 Ubuntu 22.04 LTS AMI ID (참고)

- **ap-northeast-2 (서울)**: `ami-0c55b159cbfafe1f0` (예시, 변경될 수 있음)
- **us-east-1**: `ami-0c55b159cbfafe1f0` (예시)

실제 AMI ID는 위의 AWS CLI 명령어로 확인하세요.

## 적용

수정된 코드를 pull한 후:

```bash
cd terraform
terraform init -upgrade
terraform plan
terraform apply
```

