# GitHub Actions CI/CD 파이프라인 설정 가이드

## 개요

GitHub Actions를 사용하여 코드가 push되면 자동으로 EC2 서버에 배포하는 파이프라인을 구성합니다.

## 구성된 Workflow

### 1. `deploy-to-ec2.yml` - 자동 배포
- **트리거**: `main` 브랜치에 push 시 자동 실행
- **기능**: EC2 서버에서 git pull 실행
- **선택적**: Docker 서비스 재시작

### 2. `terraform-deploy.yml` - Terraform 배포 (수동)
- **트리거**: 수동 실행만 (보안상)
- **기능**: Terraform plan/apply/destroy 실행

## 설정 단계

### 1단계: EC2 서버에 SSH 키 준비

#### EC2 서버에서 SSH 키 생성 (또는 기존 키 사용)

```bash
# EC2 서버에 접속
ssh -i your-key.pem ec2-user@your-ec2-ip

# GitHub Actions용 SSH 키 생성 (없는 경우)
ssh-keygen -t ed25519 -C "github-actions" -f ~/.ssh/github_actions_key -N ""

# 공개키를 authorized_keys에 추가
cat ~/.ssh/github_actions_key.pub >> ~/.ssh/authorized_keys

# 개인키 내용 확인 (이것을 GitHub Secrets에 저장)
cat ~/.ssh/github_actions_key
```

**또는 기존 SSH 키 사용:**
```bash
# 기존 키의 개인키 내용 확인
cat ~/.ssh/id_rsa
# 또는
cat ~/.ssh/id_ed25519
```

### 2단계: GitHub Secrets 설정

GitHub 저장소에서 **Settings → Secrets and variables → Actions**로 이동하여 다음 Secrets를 추가합니다:

#### 필수 Secrets

1. **`EC2_HOST`**
   - 값: EC2 서버의 공인 IP 또는 도메인
   - 예: `54.123.45.67` 또는 `ec2.example.com`

2. **`EC2_USER`**
   - 값: EC2 서버의 사용자명
   - 예: `ec2-user` (Amazon Linux) 또는 `ubuntu` (Ubuntu)

3. **`EC2_SSH_KEY`**
   - 값: EC2 서버의 SSH 개인키 전체 내용
   - 예:
     ```
     -----BEGIN OPENSSH PRIVATE KEY-----
     b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAABlwAAAAdzc2gtcn
     ...
     -----END OPENSSH PRIVATE KEY-----
     ```

#### 선택적 Secrets (Terraform 배포용)

4. **`AWS_ACCESS_KEY_ID`**
   - 값: AWS 액세스 키 ID

5. **`AWS_SECRET_ACCESS_KEY`**
   - 값: AWS 시크릿 액세스 키

6. **`AWS_DEFAULT_REGION`**
   - 값: AWS 리전
   - 예: `ap-northeast-2`

### 3단계: GitHub Secrets 추가 방법

1. GitHub 저장소로 이동
2. **Settings** 클릭
3. 왼쪽 메뉴에서 **Secrets and variables** → **Actions** 클릭
4. **New repository secret** 클릭
5. Name과 Secret 값을 입력하고 **Add secret** 클릭

### 4단계: Workflow 테스트

#### 자동 배포 테스트

```bash
# 로컬에서 변경사항 커밋 & 푸시
git add .
git commit -m "GitHub Actions CI/CD 파이프라인 추가"
git push origin main
```

GitHub 저장소의 **Actions** 탭에서 workflow 실행 상태를 확인할 수 있습니다.

#### 수동 배포 테스트

1. GitHub 저장소의 **Actions** 탭으로 이동
2. **Terraform Deploy** workflow 선택
3. **Run workflow** 클릭
4. Action 선택 (plan/apply/destroy)
5. **Run workflow** 클릭

## Workflow 상세 설명

### deploy-to-ec2.yml

```yaml
on:
  push:
    branches:
      - main
```

- `main` 브랜치에 push될 때마다 자동 실행
- `workflow_dispatch`로 수동 실행도 가능

**실행 단계:**
1. 코드 체크아웃
2. SSH 키 설정
3. EC2 서버에 SSH 접속하여 git pull 실행
4. (선택적) Docker 서비스 재시작

### terraform-deploy.yml

```yaml
on:
  workflow_dispatch:
```

- 수동 실행만 가능 (보안상 자동 실행 비활성화)
- Terraform plan/apply/destroy 선택 가능

## 문제 해결

### SSH 접속 실패

**증상:**
```
Permission denied (publickey)
```

**해결:**
1. SSH 키가 올바르게 설정되었는지 확인
2. EC2 서버의 `authorized_keys`에 공개키가 추가되었는지 확인
3. EC2 보안 그룹에서 SSH 포트(22)가 열려있는지 확인

### Git pull 실패

**증상:**
```
fatal: not a git repository
```

**해결:**
1. EC2 서버에서 V2R 디렉토리가 존재하는지 확인
2. 디렉토리가 git 저장소인지 확인

### Docker 재시작 실패

**증상:**
```
docker-compose.yml 파일을 찾을 수 없습니다
```

**해결:**
- 이 오류는 `continue-on-error: true`로 설정되어 있어 workflow 실패를 유발하지 않습니다
- Docker가 필요 없는 경우 무시해도 됩니다

## 보안 권장사항

1. **SSH 키 보안**
   - GitHub Secrets에 저장된 SSH 키는 저장소에 접근할 수 있는 사용자만 볼 수 있습니다
   - 정기적으로 키를 로테이션하세요

2. **AWS 자격 증명**
   - 최소 권한 원칙에 따라 필요한 권한만 부여하세요
   - IAM 역할을 사용하는 것이 더 안전합니다 (향후 개선 가능)

3. **Terraform 상태 파일**
   - `.tfstate` 파일은 민감한 정보를 포함할 수 있으므로 버전 관리에 포함하지 마세요
   - Terraform Cloud나 S3 백엔드를 사용하는 것을 권장합니다

## 고급 설정 (선택)

### IAM 역할 사용 (EC2 Instance Profile)

SSH 키 대신 IAM 역할을 사용하는 것이 더 안전합니다:

```yaml
- name: Configure AWS credentials
  uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: arn:aws:iam::ACCOUNT_ID:role/GitHubActionsRole
    aws-region: ap-northeast-2
```

### Terraform 백엔드 설정

`.terraform/` 디렉토리를 S3에 저장:

```hcl
terraform {
  backend "s3" {
    bucket = "v2r-terraform-state"
    key    = "terraform.tfstate"
    region = "ap-northeast-2"
  }
}
```

## 참고

- GitHub Actions 문서: https://docs.github.com/en/actions
- Terraform GitHub Actions: https://github.com/hashicorp/setup-terraform

