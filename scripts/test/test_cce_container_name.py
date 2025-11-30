#!/usr/bin/env python3
"""CCE 점검 컨테이너명 확인 테스트"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.database import get_db
from src.database.repository import CCECheckResultRepository

print("=" * 60)
print("CCE 점검 컨테이너명 확인")
print("=" * 60)

db = get_db()
with db.get_session() as session:
    repo = CCECheckResultRepository(session)
    sessions = repo.get_recent_sessions(5)
    
    print(f"최근 세션 수: {len(sessions)}")
    
    if sessions:
        results = repo.get_by_session(sessions[0])
        if results:
            result = results[0]
            print(f"\n✅ CCE 결과 조회: {len(results)}개")
            print(f"✅ 컨테이너명: {getattr(result, 'container_name', None)}")
            print(f"✅ 점검 대상: {getattr(result, 'target_name', None)}")
            print(f"✅ 세션 ID: {result.check_session_id}")
        else:
            print("\n⚠️  결과가 없습니다.")
    else:
        print("\n⚠️  세션이 없습니다.")

