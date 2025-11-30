# SSH 키 설정

## 주의사항
이 디렉토리에는 실제 SSH 키 파일이 저장됩니다.

## 생성 방법

### 1. SSH 키 생성
```bash
ssh-keygen -t rsa -b 4096 -f id_rsa -N ""
```

### 2. 공개키 확인
```bash
cat id_rsa.pub
```

## 파일 구조
```
keys/
├── id_rsa      # 프라이빗 키 (절대 공유하지 마세요)
├── id_rsa.pub  # 공개키 (Terraform에서 사용)
└── README.md   # 이 파일
```

## 보안 주의사항
- `id_rsa`는 `.gitignore`에 포함되어 있어야 합니다
- 절대 이 키를 Git에 커밋하지 마세요
- 프로덕션 환경에서는 다른 키를 사용하세요

