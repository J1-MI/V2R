#!/usr/bin/env python3
"""CCE 점검 수정 사항 테스트"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.cce.checker import find_cve_lab_containers
from src.database import get_db
from src.database.models import CCECheckResult

print("=" * 60)
print("CCE 점검 수정 사항 테스트")
print("=" * 60)
print()

# 1. 컨테이너 조회 테스트
print("1. Docker 컨테이너 조회 테스트")
print("-" * 60)
try:
    containers = find_cve_lab_containers()
    print(f"✅ 발견된 컨테이너: {len(containers)}개")
    for c in containers:
        service_name = c['service_name']
        print(f"  - {c['name']} ({service_name})")
except Exception as e:
    print(f"❌ 오류: {str(e)}")
print()

# 2. 모델 필드 확인
print("2. CCECheckResult 모델 필드 확인")
print("-" * 60)
try:
    db = get_db()
    with db.get_session() as session:
        result = session.query(CCECheckResult).first()
        if result:
            print(f"✅ container_name 필드 존재: {hasattr(result, 'container_name')}")
            print(f"✅ container_name 값: {getattr(result, 'container_name', None)}")
        else:
            print("⚠️  CCE 점검 결과가 없습니다.")
except Exception as e:
    print(f"❌ 오류: {str(e)}")
print()

print("=" * 60)
print("테스트 완료")
print("=" * 60)

