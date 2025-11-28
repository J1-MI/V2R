# AWS 자격 증명 설정 가이드

## 문제

Terraform이 AWS API에 접근하기 위해 자격 증명이 필요합니다.

## 해결 방법

### 방법 1: 환경 변수 설정 (빠른 방법)

EC2 서버에서 다음 명령어를 실행하세요:

```bash
export AWS_ACCESS_KEY_ID=your_access_key_id
export AWS_SECRET_ACCESS_KEY=your_secret_access_key
export AWS_DEFAULT_REGION=ap-northeast-2

# 확인
echo $AWS_ACCESS_KEY_ID
echo $AWS_DEFAULT_REGION
```

### 방법 2: AWS CLI 설정 (권장)

```bash
# AWS CLI 설치 (없는 경우)
sudo yum install aws-cli -y
# 또는
sudo apt-get install awscli -y

# 자격 증명 설정
aws configure
```

설정할 내용:
- AWS Access Key ID: `your_access_key_id`
- AWS Secret Access Key: `your_secret_access_key`
- Default region name: `ap-northeast-2`
- Default output format: `json`

### 방법 3: 자격 증명 파일 생성

```bash
mkdir -p ~/.aws
cat > ~/.aws/credentials << EOF
[default]
aws_access_key_id = your_access_key_id
aws_secret_access_key = your_secret_access_key
EOF

cat > ~/.aws/config << EOF
[default]
region = ap-northeast-2
output = json
EOF

chmod 600 ~/.aws/credentials
chmod 600 ~/.aws/config
```

### 방법 4: IAM 역할 사용 (가장 안전한 방법)

EC2 인스턴스에 IAM 역할을 연결하면 자격 증명을 직접 관리할 필요가 없습니다.

#### IAM 역할 생성 (AWS 콘솔에서)

1. IAM 콘솔 → Roles → Create role
2. Trusted entity: AWS service → EC2
3. 권한 정책 추가:
   - `AmazonEC2FullAccess` (또는 필요한 권한만)
   - `AmazonVPCFullAccess`
   - `AmazonS3FullAccess` (S3 사용 시)
4. Role name: `v2r-terraform-role`
5. Create role

#### EC2 인스턴스에 역할 연결

```bash
# AWS CLI로 역할 연결 (또는 AWS 콘솔에서)
aws ec2 associate-iam-instance-profile \
  --instance-id i-xxxxxxxxxxxxx \
  --iam-instance-profile Name=v2r-terraform-profile
```

또는 Terraform으로 역할을 연결할 수 있습니다 (추후 개선 가능).

## 자격 증명 확인

설정 후 다음 명령어로 확인:

```bash
# 환경 변수 확인
env | grep AWS

# AWS CLI로 확인
aws sts get-caller-identity

# Terraform으로 확인
cd terraform
terraform init
terraform plan
```

## 보안 주의사항

⚠️ **중요**: 

1. **자격 증명 파일 권한**
   ```bash
   chmod 600 ~/.aws/credentials
   chmod 600 ~/.aws/config
   ```

2. **환경 변수 노출 방지**
   - `.bash_history`에 저장되지 않도록 주의
   - 스크립트에 하드코딩하지 마세요

3. **최소 권한 원칙**
   - 필요한 권한만 부여
   - IAM 역할 사용 권장

## 빠른 설정 (임시)

테스트 목적으로 빠르게 설정하려면:

```bash
# 현재 세션에서만 유효
export AWS_ACCESS_KEY_ID=your_access_key_id
export AWS_SECRET_ACCESS_KEY=your_secret_access_key
export AWS_DEFAULT_REGION=ap-northeast-2

# Terraform 실행
cd terraform
terraform apply
```

## 영구 설정

모든 세션에서 사용하려면:

```bash
# ~/.bashrc 또는 ~/.bash_profile에 추가
echo 'export AWS_ACCESS_KEY_ID=your_access_key_id' >> ~/.bashrc
echo 'export AWS_SECRET_ACCESS_KEY=your_secret_access_key' >> ~/.bashrc
echo 'export AWS_DEFAULT_REGION=ap-northeast-2' >> ~/.bashrc

# 적용
source ~/.bashrc
```

## 문제 해결

### "No valid credential sources found"

- 환경 변수가 설정되었는지 확인: `echo $AWS_ACCESS_KEY_ID`
- AWS CLI 설정 확인: `aws configure list`
- 자격 증명 파일 확인: `cat ~/.aws/credentials`

### "Access Denied"

- IAM 사용자/역할에 필요한 권한이 있는지 확인
- 정책에 다음 권한이 필요:
  - EC2: `ec2:*`
  - VPC: `ec2:*` (VPC 관련)
  - S3: `s3:*` (S3 사용 시)

