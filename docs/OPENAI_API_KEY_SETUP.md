# OpenAI API 키 설정 가이드

## 설정 방법

### 방법 1: .env 파일 사용 (권장)

프로젝트 루트 디렉토리에 `.env` 파일을 생성하고 API 키를 추가합니다.

#### 1. .env 파일 생성

```bash
# 프로젝트 루트에서
cd /home/ec2-user/V2R
nano .env
```

또는:

```bash
cat > .env << EOF
OPENAI_API_KEY=sk-your-api-key-here
LLM_MODEL=gpt-4.1-nano
EOF
```

#### 2. .env 파일 내용

```
OPENAI_API_KEY=sk-your-api-key-here
LLM_MODEL=gpt-4.1-nano
```

**주의사항:**
- `sk-`로 시작하는 전체 API 키를 입력하세요
- 따옴표 없이 입력하세요
- 공백이나 줄바꿈이 없어야 합니다

#### 3. Docker Compose 재시작

```bash
# 컨테이너 재시작 (환경 변수 적용)
docker-compose down
docker-compose up -d

# 또는 컨테이너만 재시작
docker-compose restart app
```

### 방법 2: 환경 변수로 직접 설정

```bash
# 현재 세션에서만 유효
export OPENAI_API_KEY=sk-your-api-key-here
export LLM_MODEL=gpt-4.1-nano

# Docker Compose 실행
docker-compose up -d
```

### 방법 3: docker-compose.yml 직접 수정 (비권장)

`docker-compose.yml` 파일을 직접 수정할 수도 있지만, 보안상 권장하지 않습니다.

## 설정 확인

### 1. 환경 변수 확인

```bash
# 컨테이너 내부에서 확인
docker-compose exec app env | grep OPENAI
```

예상 출력:
```
OPENAI_API_KEY=sk-...
LLM_MODEL=gpt-4.1-nano
```

### 2. Python에서 확인

```bash
# 컨테이너 내부에서
docker-compose exec app python -c "from src.config import OPENAI_API_KEY; print('API Key:', OPENAI_API_KEY[:10] + '...' if OPENAI_API_KEY else 'Not set')"
```

### 3. LLM 리포트 생성 테스트

```bash
# 리포트 생성 스크립트 실행
docker-compose exec app python -c "
from src.llm.report_generator import LLMReportGenerator
generator = LLMReportGenerator()
if generator.client:
    print('✓ OpenAI API 키 설정 성공!')
else:
    print('✗ OpenAI API 키 설정 실패')
"
```

## 보안 주의사항

### ⚠️ 중요

1. **`.env` 파일을 Git에 커밋하지 마세요**
   - `.gitignore`에 `.env`가 포함되어 있는지 확인
   - API 키가 공개 저장소에 노출되면 즉시 키를 재발급하세요

2. **파일 권한 설정**
   ```bash
   chmod 600 .env  # 소유자만 읽기/쓰기 가능
   ```

3. **API 키 보호**
   - API 키를 절대 공유하지 마세요
   - 로그 파일에 출력되지 않도록 주의하세요
   - 필요시 API 키에 사용량 제한을 설정하세요

## 문제 해결

### API 키가 인식되지 않는 경우

1. **.env 파일 위치 확인**
   ```bash
   # 프로젝트 루트에 있어야 함
   ls -la .env
   ```

2. **Docker Compose 재시작**
   ```bash
   docker-compose down
   docker-compose up -d
   ```

3. **환경 변수 확인**
   ```bash
   docker-compose exec app env | grep OPENAI
   ```

4. **로그 확인**
   ```bash
   docker-compose logs app | grep -i openai
   ```

### API 키 형식 오류

- API 키는 `sk-`로 시작해야 합니다
- 공백이나 줄바꿈이 포함되지 않아야 합니다
- 따옴표 없이 입력하세요

### API 호출 실패

- API 키가 유효한지 확인
- 사용량 제한을 초과하지 않았는지 확인
- 네트워크 연결 확인

## 사용 예시

API 키 설정 후 리포트 생성:

```bash
# 대시보드에서 리포트 생성
docker-compose exec app streamlit run src/dashboard/app.py \
  --server.port 8501 \
  --server.address 0.0.0.0
```

또는 스크립트로 직접 생성:

```python
from src.llm.report_generator import LLMReportGenerator
from src.database import get_db

db = get_db()
with db.get_session() as session:
    # 스캔 결과 조회
    # ...
    
    # 리포트 생성
    generator = LLMReportGenerator()
    summary = generator.generate_executive_summary(scan_results, poc_reproductions)
```

## 참고

- OpenAI API 문서: https://platform.openai.com/docs
- API 키 발급: https://platform.openai.com/api-keys
- 사용량 모니터링: https://platform.openai.com/usage

