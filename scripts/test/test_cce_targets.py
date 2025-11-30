#!/usr/bin/env python3
"""
CCE 점검 대상 브리핑 스크립트
"""

import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.database import get_db
from src.database.repository import CCECheckResultRepository
from collections import Counter

def main():
    """점검 대상 브리핑"""
    print("=" * 60)
    print("CCE 점검 대상 브리핑")
    print("=" * 60)
    print()
    
    db = get_db()
    with db.get_session() as session:
        repo = CCECheckResultRepository(session)
        
        # 최근 세션 조회
        sessions = repo.get_recent_sessions(20)
        
        if not sessions:
            print("❌ 점검 결과가 없습니다.")
            return
        
        print(f"📊 총 세션 수: {len(sessions)}개")
        print()
        
        # 세션별 상세 정보
        print("📋 세션별 상세 정보:")
        print("-" * 60)
        for i, session_id in enumerate(sessions[:10], 1):
            info = repo.get_session_info(session_id)
            if info:
                target = info['target_name'] or "알 수 없음"
                timestamp = info['check_timestamp'].strftime("%Y-%m-%d %H:%M:%S") if info['check_timestamp'] else "N/A"
                total = info['total_checks']
                print(f"{i}. 세션: {session_id}")
                print(f"   점검 대상: {target}")
                print(f"   점검 시간: {timestamp}")
                print(f"   점검 항목: {total}개")
                print()
        
        # 점검 대상 통계
        print("=" * 60)
        print("📈 점검 대상 통계")
        print("=" * 60)
        targets = []
        for session_id in sessions:
            info = repo.get_session_info(session_id)
            if info and info['target_name']:
                targets.append(info['target_name'])
        
        if targets:
            counter = Counter(targets)
            for target, count in counter.most_common():
                print(f"  • {target}: {count}회 점검")
        else:
            print("  점검 대상 정보가 없습니다.")
        
        print()
        
        # 최신 세션 정보
        latest_session = repo.get_latest_session()
        if latest_session:
            latest_info = repo.get_session_info(latest_session)
            if latest_info:
                print("=" * 60)
                print("🔄 최신 점검 세션")
                print("=" * 60)
                print(f"  세션 ID: {latest_info['session_id']}")
                print(f"  점검 대상: {latest_info['target_name'] or '알 수 없음'}")
                print(f"  점검 시간: {latest_info['check_timestamp'].strftime('%Y-%m-%d %H:%M:%S') if latest_info['check_timestamp'] else 'N/A'}")
                print(f"  총 점검 항목: {latest_info['total_checks']}개")
                print()
        
        # 통계 요약
        print("=" * 60)
        print("📊 전체 통계 요약")
        print("=" * 60)
        all_results = []
        for session_id in sessions:
            results = repo.get_by_session(session_id)
            all_results.extend(results)
        
        if all_results:
            total = len(all_results)
            by_result = Counter([r.result for r in all_results])
            by_severity = Counter([r.severity for r in all_results if r.severity])
            
            print(f"  총 점검 결과: {total}개")
            print(f"  결과 분포:")
            for result, count in by_result.most_common():
                print(f"    - {result}: {count}개")
            print(f"  심각도 분포:")
            for severity in sorted(by_severity.keys(), reverse=True):
                print(f"    - 심각도 {severity}: {by_severity[severity]}개")
        
        print()
        print("=" * 60)
        print("✅ 브리핑 완료")
        print("=" * 60)

if __name__ == "__main__":
    main()

