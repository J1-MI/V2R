# CCE 점검 결과 대시보드 테스트 가이드

## 테스트 명령어

### 1. 데이터베이스 초기화 (테이블 생성)
```bash
docker exec v2r-app python3 scripts/utils/reset_db.py
```

### 2. CCE 점검 결과 테스트 데이터 삽입
```bash
docker exec v2r-app python3 scripts/test/test_cce_insert.py
```

### 3. 대시보드 확인
브라우저에서 다음 URL로 접속:
```
http://localhost:8501
```

대시보드에서 "CCE 점검 결과" 탭을 선택하여 결과를 확인하세요.

## 예상 결과

- 총 점검 항목: 8개
- 양호: 5개
- 취약: 2개
- 해당 없음: 1개

## 추가 테스트 데이터 삽입

같은 명령어를 다시 실행하면 새로운 세션으로 추가 데이터가 삽입됩니다.

