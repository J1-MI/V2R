#!/usr/bin/env python3
"""CCE 세션 조회 테스트"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.database import get_db
from src.database.repository import CCECheckResultRepository
from sqlalchemy import text

print("=" * 60)
print("CCE 세션 조회 테스트")
print("=" * 60)

db = get_db()
with db.get_session() as session:
    # 직접 SQL로 조회
    print("\n1. 직접 SQL 조회:")
    result = session.execute(text('''
        SELECT DISTINCT check_session_id, target_name, MIN(check_timestamp) as first_check 
        FROM cce_check_results 
        GROUP BY check_session_id, target_name 
        ORDER BY first_check DESC 
        LIMIT 20
    '''))
    rows = result.fetchall()
    print(f"   총 세션 수: {len(rows)}")
    for r in rows:
        print(f"   - {r[0]} ({r[1]})")
    
    # Repository 메서드로 조회
    print("\n2. Repository.get_recent_sessions() 조회:")
    repo = CCECheckResultRepository(session)
    sessions = repo.get_recent_sessions(20)
    print(f"   총 세션 수: {len(sessions)}")
    for s in sessions:
        print(f"   - {s}")
    
    # 각 세션의 정보 조회
    print("\n3. 각 세션 정보:")
    for session_id in sessions[:5]:
        info = repo.get_session_info(session_id)
        if info:
            print(f"   - {session_id}: {info['target_name']} ({info['total_checks']}개 항목)")

