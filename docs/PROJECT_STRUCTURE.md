# 프로젝트 구조

```
V2R/
├── .gitignore              # Git 무시 파일
├── README.md               # 프로젝트 메인 문서
├── PROJECT_KANBAN.md       # Kanban 보드
├── PROJECT_STRUCTURE.md    # 이 파일
├── requirements.txt        # Python 의존성
│
├── terraform/              # Terraform 인프라 코드
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   ├── vpc.tf             # VPC/서브넷/보안그룹
│   ├── ec2.tf             # EC2 인스턴스
│   ├── s3.tf              # S3 버킷
│   ├── versions.tf
│   ├── keys/              # SSH 키 (로컬 전용)
│   │   └── README.md
│   ├── user_data/         # EC2 user_data 스크립트
│   │   ├── web_server.sh
│   │   └── scanner.sh
│   └── README.md
│
├── src/                   # 소스 코드
│   ├── __init__.py
│   ├── config.py          # 설정 관리
│   │
│   ├── scanner/          # 스캐너 통합
│   │   ├── __init__.py
│   │   ├── nmap_scanner.py
│   │   ├── nuclei_scanner.py
│   │   └── normalizer.py  # 결과 정규화
│   │
│   ├── poc/              # PoC 재현 엔진
│   │   ├── __init__.py
│   │   ├── isolation.py  # 격리 환경
│   │   ├── reproduction.py
│   │   └── evidence.py   # 증거 수집
│   │
│   ├── verification/     # PoC 진위 검증
│   │   ├── __init__.py
│   │   ├── static_analyzer.py
│   │   ├── behavior_matcher.py
│   │   └── reliability.py  # 신뢰도 점수화
│   │
│   ├── ml/               # ML 우선순위
│   │   ├── __init__.py
│   │   ├── priority_model.py
│   │   └── feature_extractor.py
│   │
│   ├── llm/              # LLM 리포트 생성
│   │   ├── __init__.py
│   │   ├── advisor.py
│   │   └── report_generator.py
│   │
│   ├── report/           # 리포트 자동화
│   │   ├── __init__.py
│   │   ├── template.py
│   │   ├── generator.py
│   │   └── pr_template.py
│   │
│   ├── database/         # 데이터베이스 관련
│   │   ├── __init__.py
│   │   ├── connection.py
│   │   ├── models.py
│   │   └── schema.sql
│   │
│   └── dashboard/       # 대시보드
│       ├── __init__.py
│       └── app.py       # Streamlit 앱
│
├── scripts/              # 유틸리티 스크립트
│   ├── deployment/      # 배포 스크립트
│   ├── scanning/        # 스캐닝 스크립트
│   ├── poc/             # PoC 관련
│   └── utils/           # 유틸리티
│
├── docs/                 # 문서
│   ├── POC_LIST.md      # PoC 목록
│   ├── API.md           # API 문서
│   └── DEPLOYMENT.md    # 배포 가이드
│
├── tests/                # 테스트
│   ├── unit/
│   ├── integration/
│   └── fixtures/
│
└── evidence/            # 증거 파일 (로컬, .gitignore)
    ├── pcap/
    ├── logs/
    └── screenshots/
```

## 주요 디렉토리 설명

### terraform/
AWS 인프라를 Terraform으로 정의합니다.

### src/
모든 Python 소스 코드를 포함합니다.
- `scanner/`: 다양한 스캐너 통합 및 정규화
- `poc/`: PoC 재현 및 증거 수집
- `verification/`: PoC 진위 검증
- `ml/`: ML 모델 및 우선순위 계산
- `llm/`: LLM 기반 리포트 생성
- `report/`: 리포트 자동화
- `database/`: DB 연결 및 모델
- `dashboard/`: Streamlit 대시보드

### scripts/
자동화 스크립트 및 유틸리티

### docs/
프로젝트 문서

### tests/
단위 테스트 및 통합 테스트

