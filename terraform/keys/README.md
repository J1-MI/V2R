# SSH 키 생성 가이드

## SSH 키 생성

SSH 키가 없으면 Terraform 배포 시 오류가 발생합니다. 다음 명령어로 키를 생성하세요:

```bash
# terraform 디렉토리에서 실행
cd terraform
mkdir -p keys
ssh-keygen -t rsa -b 4096 -f keys/id_rsa -N ""

# 생성 확인
ls -la keys/
```

## 키 없이 배포하는 방법

키가 없으면 EC2 인스턴스는 키 없이 생성됩니다. 이후 접속 방법:
- AWS Systems Manager Session Manager 사용
- AWS 콘솔에서 키 페어 연결
- 또는 키를 수동으로 추가

## 주의사항

- `keys/id_rsa` (개인키)는 절대 공유하거나 버전 관리에 포함하지 마세요
- `.gitignore`에 `keys/` 디렉토리가 포함되어 있는지 확인하세요
