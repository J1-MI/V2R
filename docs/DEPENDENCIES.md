# 의존성 패키지 목록

## 개요
V2R 프로젝트에서 사용하는 Python 및 시스템 의존성 패키지 목록입니다.

## Python 패키지 의존성

### AWS SDK
- **boto3** (>=1.34.0): AWS 서비스 Python SDK
- **botocore** (>=1.34.0): boto3의 핵심 라이브러리

### 네트워크 스캐닝
- **python-nmap** (>=0.7.1): Nmap 포트 스캐너 Python 래퍼
- **requests** (>=2.31.0): HTTP 라이브러리

### 데이터 처리
- **pandas** (>=2.1.0): 데이터 분석 및 조작
- **numpy** (>=1.24.0): 수치 계산 라이브러리

### 데이터베이스
- **sqlalchemy** (>=2.0.0): ORM 및 데이터베이스 추상화
- **psycopg2-binary** (>=2.9.0): PostgreSQL 어댑터

### ML/LLM
- **openai** (>=1.0.0): OpenAI API 클라이언트
- **scikit-learn** (>=1.3.0): 머신러닝 라이브러리
- **xgboost** (>=2.0.0): 그래디언트 부스팅 라이브러리

### 리포트 생성
- **python-docx** (>=1.1.0): Word 문서 생성
- **reportlab** (>=4.0.0): PDF 생성 라이브러리

### 웹 대시보드
- **streamlit** (>=1.28.0): 웹 대시보드 프레임워크

### 유틸리티
- **python-dotenv** (>=1.0.0): 환경 변수 관리 (.env 파일)
- **pyyaml** (>=6.0): YAML 파일 파싱
- **jinja2** (>=3.1.0): 템플릿 엔진

### 테스트
- **pytest** (>=7.4.0): 테스트 프레임워크
- **pytest-cov** (>=4.1.0): 코드 커버리지 도구

### 개발 도구 (Dockerfile.dev에만)
- **black**: 코드 포맷터
- **flake8**: 린터
- **ipython**: 향상된 Python 인터프리터
- **ipdb**: 디버거

## 시스템 패키지 (Docker 이미지에 포함)

### 기본 도구
- **build-essential**: 컴파일 도구
- **curl, wget**: 파일 다운로드 도구
- **git**: 버전 관리
- **vim**: 텍스트 에디터

### 보안 스캐닝 도구
- **nmap**: 네트워크 스캐너 (시스템 패키지)
- **nuclei**: 취약점 스캐너 (컨테이너 빌드 시 자동 설치)
- **postgresql-client**: PostgreSQL 클라이언트 도구

## 설치 방법

### 로컬 환경
```bash
pip install -r requirements.txt
```

### Docker 환경 (권장)
```bash
# Docker 이미지 빌드 시 자동 설치됨
docker-compose build
```

## 의존성 확인

### 설치된 패키지 확인
```bash
# 로컬 환경
pip list

# Docker 환경
docker-compose exec app pip list
```

### requirements.txt 업데이트
```bash
# 현재 설치된 패키지로 requirements.txt 생성
pip freeze > requirements.txt
```

## 의존성 버전 관리

- **고정 버전**: 프로덕션 환경에서는 버전을 고정하는 것을 권장합니다
- **최소 버전**: 현재는 최소 버전만 명시하여 유연성 확보
- **보안 업데이트**: 정기적으로 `pip list --outdated`로 확인 후 업데이트

## 문제 해결

### 패키지 설치 실패
```bash
# 캐시 클리어 후 재설치
pip cache purge
pip install --no-cache-dir -r requirements.txt
```

### 버전 충돌
```bash
# 가상환경 사용 권장
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

