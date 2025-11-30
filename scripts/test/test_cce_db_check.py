#!/usr/bin/env python3
"""CCE 점검 결과 DB 확인"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.database import get_db
from sqlalchemy import text

print("=" * 60)
print("CCE 점검 결과 DB 확인")
print("=" * 60)

db = get_db()
with db.get_session() as session:
    # 모든 세션 조회
    result = session.execute(text('''
        SELECT 
            check_session_id, 
            target_name, 
            container_name, 
            COUNT(*) as cnt,
            MIN(check_timestamp) as first_check,
            MAX(check_timestamp) as last_check
        FROM cce_check_results 
        GROUP BY check_session_id, target_name, container_name 
        ORDER BY first_check DESC
    '''))
    rows = result.fetchall()
    print(f"\n총 세션 수: {len(rows)}")
    print("\n세션별 상세:")
    for r in rows:
        print(f"  - {r[0]}")
        print(f"    대상: {r[1]}")
        print(f"    컨테이너: {r[2]}")
        print(f"    항목 수: {r[3]}개")
        print(f"    시간: {r[4]} ~ {r[5]}")
        print()

