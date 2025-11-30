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
        task_type: 작업 타입 (DOCKER_STATUS, FULL_SCAN, CCE_CHECK)
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

