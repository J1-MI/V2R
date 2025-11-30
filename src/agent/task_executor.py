"""
작업 실행 모듈
Agent가 받은 작업을 실행하고 결과를 반환
"""

import logging
from typing import Dict, Any

from src.scanner.docker_lab import get_docker_status, run_full_scan, run_cce_check

logger = logging.getLogger(__name__)


def execute_task(task_type: str, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    작업 실행
    
    Args:
        task_type: 작업 타입 (DOCKER_STATUS, FULL_SCAN, CCE_CHECK, DB_INIT)
        parameters: 작업 파라미터
    
    Returns:
        작업 결과 딕셔너리
        {
            "success": bool,
            "result": dict,
            "error": str (optional)
        }
    """
    if parameters is None:
        parameters = {}
    
    try:
        if task_type == "DOCKER_STATUS":
            logger.info("Docker 상태 조회 작업 실행")
            result = get_docker_status()
            return {
                "success": result.get("success", False),
                "result": result,
                "error": result.get("error")
            }
        
        elif task_type == "FULL_SCAN":
            logger.info("전체 스캔 작업 실행")
            fast_mode = parameters.get("fast_mode", True)
            enable_poc = parameters.get("enable_poc", True)
            enable_cce = parameters.get("enable_cce", False)
            
            result = run_full_scan(
                fast_mode=fast_mode,
                enable_poc=enable_poc,
                enable_cce=enable_cce
            )
            return {
                "success": result.get("success", False),
                "result": result,
                "error": result.get("error")
            }
        
        elif task_type == "CCE_CHECK":
            logger.info("CCE 점검 작업 실행")
            data_json_path = parameters.get("data_json_path")
            
            result = run_cce_check(data_json_path)
            return {
                "success": result.get("success", False),
                "result": result,
                "error": result.get("error")
            }
        
        elif task_type == "DB_INIT":
            logger.info("DB 초기화 작업 실행")
            return execute_db_init()
        
        else:
            return {
                "success": False,
                "error": f"알 수 없는 작업 타입: {task_type}"
            }
    
    except Exception as e:
        logger.error(f"작업 실행 실패: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


def execute_db_init() -> Dict[str, Any]:
    """
    데이터베이스 초기화 실행
    
    Returns:
        초기화 결과 딕셔너리
    """
    try:
        from src.database import initialize_database, get_db
        from sqlalchemy import text
        
        db = get_db()
        
        # 연결 테스트
        if not db.test_connection():
            return {
                "success": False,
                "error": "데이터베이스 연결 실패"
            }
        
        result_messages = []
        
        # 기존 테이블 삭제
        logger.info("기존 테이블 삭제 중...")
        try:
            with db.get_session() as session:
                # 외래 키 제약 조건 비활성화
                session.execute(text("SET session_replication_role = 'replica';"))
                
                # 모든 테이블 삭제
                tables = [
                    "agent_tasks", "agents", "cce_check_results",
                    "poc_reproductions", "poc_metadata", "scan_results",
                    "reports", "events"
                ]
                
                for table in tables:
                    try:
                        session.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE;"))
                        result_messages.append(f"✓ 테이블 삭제: {table}")
                    except Exception as e:
                        logger.warning(f"테이블 삭제 실패 ({table}): {str(e)}")
                        result_messages.append(f"⚠️ 테이블 삭제 실패 ({table}): {str(e)}")
                
                # 트리거 함수 삭제
                try:
                    session.execute(text("DROP FUNCTION IF EXISTS update_updated_at_column() CASCADE;"))
                    result_messages.append("✓ 트리거 함수 삭제")
                except Exception as e:
                    logger.warning(f"트리거 함수 삭제 실패: {str(e)}")
                
                session.commit()
        except Exception as e:
            logger.error(f"테이블 삭제 중 오류: {str(e)}")
            result_messages.append(f"⚠️ 테이블 삭제 중 오류: {str(e)}")
        
        # 스키마 재생성
        logger.info("스키마 재생성 중...")
        if initialize_database():
            result_messages.append("✓ 데이터베이스 스키마 재생성 완료")
            return {
                "success": True,
                "result": {
                    "message": "데이터베이스 초기화 완료",
                    "details": result_messages
                }
            }
        else:
            return {
                "success": False,
                "error": "스키마 재생성 실패",
                "result": {
                    "details": result_messages
                }
            }
    
    except Exception as e:
        logger.error(f"DB 초기화 실패: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return {
            "success": False,
            "error": str(e)
        }

