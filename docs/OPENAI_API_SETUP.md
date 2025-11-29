# OpenAI API 키 설정 가이드

## 개요

V2R 프로젝트에서 LLM 리포트 생성 기능을 사용하려면 OpenAI API 키가 필요합니다.

## 현재 상태 확인

로그에서 다음 메시지가 보이면 API 키가 설정되지 않은 것입니다:
```
WARNING - OpenAI API key not provided
```

## 설정 방법

### 방법 1: .env 파일 사용 (권장)

#### 1. .env 파일 생성/편집

프로젝트 루트 디렉토리에 `.env` 파일을 생성하거나 편집합니다:

```bash
# Windows PowerShell
notepad .env

# 또는 직접 생성
echo "OPENAI_API_KEY=your-api-key-here" > .env
```

#### 2. .env 파일 내용

```env
# OpenAI API 설정
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# LLM 모델 선택 (선택사항)
LLM_MODEL=gpt-4
# 또는
# LLM_MODEL=gpt-3.5-turbo  # 더 저렴한 옵션
```

#### 3. Docker 컨테이너 재시작

`.env` 파일을 수정한 후 Docker 컨테이너를 재시작해야 합니다:

```powershell
# 컨테이너 재시작
docker-compose down
docker-compose up -d

# 또는 app 컨테이너만 재시작
docker-compose restart app
```

### 방법 2: docker-compose.yml 직접 수정

`docker-compose.yml`의 `app` 서비스 환경 변수에 직접 추가:

```yaml
services:
  app:
    environment:
      # LLM 설정
      OPENAI_API_KEY: sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
      LLM_MODEL: gpt-4
```

그 후 재시작:
```powershell
docker-compose up -d
```

### 방법 3: 환경 변수로 직접 전달

```powershell
# PowerShell에서
$env:OPENAI_API_KEY = "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
docker-compose up -d
```

## API 키 확인

### 1. 컨테이너 내부에서 확인

```powershell
# 환경 변수 확인
docker-compose exec app python -c "import os; print('API Key:', '설정됨' if os.getenv('OPENAI_API_KEY') else '설정 안됨')"
```

### 2. Python 코드로 확인

```powershell
docker-compose exec app python -c "
from src.config import OPENAI_API_KEY
if OPENAI_API_KEY:
    print('✅ OpenAI API 키가 설정되어 있습니다.')
    print('키 길이:', len(OPENAI_API_KEY))
else:
    print('❌ OpenAI API 키가 설정되지 않았습니다.')
"
```

### 3. 리포트 생성 테스트

```powershell
docker-compose exec app python -c "
from src.llm.report_generator import LLMReportGenerator
generator = LLMReportGenerator()
if generator.client:
    print('✅ OpenAI 클라이언트 초기화 성공')
else:
    print('❌ OpenAI 클라이언트 초기화 실패 - API 키 확인 필요')
"
```

## OpenAI API 키 발급 방법

### 1. OpenAI 계정 생성

1. [OpenAI 웹사이트](https://platform.openai.com/) 접속
2. 계정 생성 또는 로그인

### 2. API 키 생성

1. 대시보드에서 "API keys" 메뉴 선택
2. "Create new secret key" 클릭
3. 키 이름 입력 (예: "V2R Project")
4. 생성된 키 복사 (한 번만 표시됨!)

### 3. 키 형식

OpenAI API 키는 다음과 같은 형식입니다:3`    
```
sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

## 비용 고려사항

### 모델별 가격 (2024년 기준)

- **GPT-4**: 더 정확하지만 비쌈
- **GPT-3.5-turbo**: 저렴하고 빠름 (대부분의 경우 충분)

### 비용 절감 팁

1. **GPT-3.5-turbo 사용**: 리포트 생성에는 충분합니다
   ```env
   LLM_MODEL=gpt-3.5-turbo
   ```

2. **사용량 모니터링**: OpenAI 대시보드에서 사용량 확인

3. **캐싱 활용**: 동일한 스캔 결과에 대해서는 리포트 재생성 시 캐시 사용

## 문제 해결

### API 키가 인식되지 않는 경우

1. **.env 파일 위치 확인**
   ```powershell
   # 프로젝트 루트에 .env 파일이 있는지 확인
   ls .env
   ```

2. **환경 변수 확인**
   ```powershell
   docker-compose exec app env | findstr OPENAI
   ```

3. **컨테이너 재시작**
   ```powershell
   docker-compose restart app
   ```

### API 키 형식 오류

- 키는 `sk-`로 시작해야 합니다
- 공백이나 줄바꿈이 포함되지 않았는지 확인

### API 호출 실패

1. **인터넷 연결 확인**: 컨테이너에서 OpenAI API에 접근 가능한지 확인
2. **API 키 유효성 확인**: OpenAI 대시보드에서 키 상태 확인
3. **할당량 확인**: API 사용량 한도 확인

## 테스트

API 키 설정 후 리포트 생성 테스트:

```powershell
# 전체 테스트 실행
docker-compose exec app python scripts/test/run_full_test.py

# 리포트 생성 부분에서 다음 메시지가 보여야 함:
# INFO - OpenAI client initialized (model: gpt-4)
```

## 보안 주의사항

⚠️ **중요**: `.env` 파일은 절대 Git에 커밋하지 마세요!

- `.gitignore`에 `.env`가 포함되어 있는지 확인
- API 키를 코드에 하드코딩하지 마세요
- 공유 시 API 키를 제거하세요

## 다음 단계

API 키 설정 후:
1. 리포트 생성 테스트
2. 대시보드에서 리포트 확인
3. Executive Summary 품질 확인



