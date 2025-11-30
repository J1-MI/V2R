# Terraform 인프라 코드

## 개요
AWS VPC 격리 환경에서 취약점 테스트베드를 구성하는 Terraform 코드입니다.

## 구조
```
terraform/
├── main.tf          # 주요 리소스 정의
├── variables.tf     # 변수 정의
├── outputs.tf      # 출력값 정의
├── vpc.tf          # VPC/서브넷/보안그룹
├── ec2.tf          # EC2 인스턴스
├── s3.tf           # S3 버킷 (증거 저장소)
└── versions.tf     # 프로바이더 버전
```

## 사용법

### 초기화
```bash
cd terraform
terraform init
```

### 계획 확인
```bash
terraform plan
```

### 적용
```bash
terraform apply
```

### 삭제
```bash
terraform destroy
```

## 주의사항
- **절대 프로덕션 환경에 적용하지 마세요**
- 격리된 VPC에서만 사용
- 비용 모니터링 필수

