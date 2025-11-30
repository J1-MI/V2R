#!/usr/bin/env python3
"""
CCE 점검 결과 테스트 데이터 삽입 스크립트
대시보드에서 CCE 점검 결과가 정상적으로 표시되는지 확인하기 위한 테스트 데이터 생성
"""

import sys
import os
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from datetime import datetime
from src.database import get_db, initialize_database
from src.database.repository import CCECheckResultRepository

def create_test_cce_data():
    """테스트용 CCE 점검 결과 데이터 생성"""
    
    # 데이터베이스 초기화 확인
    print("📊 데이터베이스 초기화 확인 중...")
    try:
        initialize_database()
        print("✅ 데이터베이스 초기화 완료")
    except Exception as e:
        print(f"⚠️ 데이터베이스 초기화 경고: {str(e)}")
    
    # 세션 ID 생성 (같은 실행에서 생성된 점검들을 그룹화)
    # 점검 대상 이름 (예: "Mongo", "Jenkins", "EC2-Server-01" 등)
    target_name = "테스트서버"  # 실제 사용 시 점검 대상으로 변경
    session_id = f"cce_{target_name.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # 테스트 데이터 생성
    test_results = [
        {
            "check_session_id": session_id,
            "target_name": target_name,
            "cce_id": "CCE-LNX-001",
            "check_name": "안전한 네트워크 모니터링 서비스 사용",
            "severity": 3,
            "result": "양호",
            "detail": "SNMPv3가 설정되어 있으며 AuthPriv 보안레벨이 적용됨",
            "check_timestamp": datetime.now()
        },
        {
            "check_session_id": session_id,
            "target_name": target_name,
            "cce_id": "CCE-LNX-002",
            "check_name": "불필요한 SMTP 서비스 실행",
            "severity": 3,
            "result": "양호",
            "detail": "25번 포트에서 SMTP 서비스가 실행되지 않음",
            "check_timestamp": datetime.now()
        },
        {
            "check_session_id": session_id,
            "target_name": target_name,
            "cce_id": "CCE-LNX-003",
            "check_name": "SMTP 서비스의 expn/vrfy 명령어 실행 제한 미비",
            "severity": 3,
            "result": "취약",
            "detail": "sendmail.cf 파일에 noexpn, novrfy 설정이 없음",
            "check_timestamp": datetime.now()
        },
        {
            "check_session_id": session_id,
            "target_name": target_name,
            "cce_id": "CCE-LNX-018",
            "check_name": "root 계정 원격 접속 제한 미비",
            "severity": 5,
            "result": "양호",
            "detail": "sshd_config에서 PermitRootLogin no로 설정됨",
            "check_timestamp": datetime.now()
        },
        {
            "check_session_id": session_id,
            "target_name": target_name,
            "cce_id": "CCE-LNX-022",
            "check_name": "취약한 서비스 활성화",
            "severity": 5,
            "result": "취약",
            "detail": "불필요한 서비스가 실행 중임: telnet, rsh",
            "check_timestamp": datetime.now()
        },
        {
            "check_session_id": session_id,
            "target_name": target_name,
            "cce_id": "CCE-LNX-037",
            "check_name": "비밀번호 관리정책 설정 미비",
            "severity": 5,
            "result": "NOT_APPLICABLE",
            "detail": "비밀번호 정책 확인 명령어 실행 실패",
            "check_timestamp": datetime.now()
        },
        {
            "check_session_id": session_id,
            "target_name": target_name,
            "cce_id": "CCE-LNX-060",
            "check_name": "계정 잠금 임계값 설정 미비",
            "severity": 2,
            "result": "양호",
            "detail": "pam_faillock.so가 설정되어 있으며 deny=5로 설정됨",
            "check_timestamp": datetime.now()
        },
        {
            "check_session_id": session_id,
            "target_name": target_name,
            "cce_id": "CCE-LNX-067",
            "check_name": "NTP 및 시각 동기화 미설정",
            "severity": 1,
            "result": "양호",
            "detail": "chronyd 서비스가 실행 중이며 NTP 서버와 동기화됨",
            "check_timestamp": datetime.now()
        }
    ]
    
    print(f"\n📝 테스트 데이터 생성 중... (세션 ID: {session_id})")
    
    # 데이터베이스에 저장
    db = get_db()
    with db.get_session() as session:
        repo = CCECheckResultRepository(session)
        
        try:
            results = repo.save_batch(test_results)
            print(f"✅ {len(results)}개의 CCE 점검 결과 저장 완료")
            
            # 통계 출력
            stats = repo.get_statistics(session_id)
            print(f"\n📊 점검 결과 통계:")
            print(f"  - 총 점검 항목: {stats['total']}")
            print(f"  - 양호: {stats['by_result'].get('양호', 0)}")
            print(f"  - 취약: {stats['by_result'].get('취약', 0)}")
            print(f"  - 해당 없음: {stats['by_result'].get('NOT_APPLICABLE', 0)}")
            
            return session_id
            
        except Exception as e:
            print(f"❌ 데이터 저장 실패: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

if __name__ == "__main__":
    print("=" * 60)
    print("CCE 점검 결과 테스트 데이터 삽입")
    print("=" * 60)
    
    session_id = create_test_cce_data()
    
    if session_id:
        print(f"\n✅ 테스트 완료!")
        print(f"📌 세션 ID: {session_id}")
        print(f"\n💡 대시보드에서 'CCE 점검 결과' 탭을 확인하세요.")
        print(f"   http://localhost:8501")
    else:
        print("\n❌ 테스트 실패")
        sys.exit(1)

