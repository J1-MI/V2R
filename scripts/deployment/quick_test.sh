#!/bin/bash
# EC2 배포 빠른 테스트 스크립트
# EC2 서버에서 실행

set -e

echo "=========================================="
echo "V2R 빠른 테스트 스크립트"
echo "=========================================="

# 1. 서비스 상태 확인
echo "1. Docker 서비스 상태 확인..."
docker-compose ps

# 2. API 서버 확인
echo ""
echo "2. API 서버 확인..."
API_RESPONSE=$(curl -s http://localhost:5000/api/agents)
echo "응답: $API_RESPONSE"

if echo "$API_RESPONSE" | grep -q "success"; then
    echo "✅ API 서버 정상 동작"
else
    echo "❌ API 서버 오류"
    echo "로그 확인: docker-compose logs api"
    exit 1
fi

# 3. 데이터베이스 확인
echo ""
echo "3. 데이터베이스 테이블 확인..."
docker exec v2r-postgres psql -U v2r -d v2r -c "\dt" | grep -E "agents|agent_tasks" || echo "⚠️  테이블이 없을 수 있습니다. init_db.py를 실행하세요."

# 4. Agent 등록 확인
echo ""
echo "4. 등록된 Agent 확인..."
AGENT_COUNT=$(echo "$API_RESPONSE" | grep -o '"agent_id"' | wc -l)
echo "등록된 Agent 수: $AGENT_COUNT"

# 5. Streamlit 대시보드 확인
echo ""
echo "5. Streamlit 대시보드 확인..."
if docker exec v2r-app ps aux | grep -q streamlit; then
    echo "✅ Streamlit 대시보드 실행 중"
else
    echo "⚠️  Streamlit 대시보드가 실행되지 않았습니다."
    echo "실행: docker exec -d v2r-app streamlit run src/dashboard/app.py --server.port 8501 --server.address 0.0.0.0"
fi

echo ""
echo "=========================================="
echo "테스트 완료"
echo "=========================================="
echo "다음 단계:"
echo "1. 로컬 PC에서 Agent 실행"
echo "2. 브라우저에서 http://$(curl -s ifconfig.me):8501 접속"
echo "3. 'Agent & Local Scanner' 페이지에서 작업 생성"
echo "=========================================="

