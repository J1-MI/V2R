"""
Docker Lab 관련 스캔 및 점검 함수
로컬 Docker 환경에서 실행되는 스캔/점검 로직을 재사용 가능한 함수로 제공
"""

import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

from src.cce.checker import (
    find_cve_lab_containers,
    run_cce_checks_for_all_containers,
    save_cce_results_to_db
)

logger = logging.getLogger(__name__)

# 프로젝트 루트 경로
project_root = Path(__file__).parent.parent.parent


def get_docker_status() -> Dict[str, Any]:
    """
    Docker 컨테이너 상태 조회
    
    Returns:
        Docker 상태 정보 딕셔너리
        {
            "success": bool,
            "containers": List[Dict[str, str]],  # 컨테이너 정보 리스트
            "total": int,
            "error": str (optional)
        }
    """
    try:
        containers = find_cve_lab_containers()
        
        return {
            "success": True,
            "containers": containers,
            "total": len(containers)
        }
    except Exception as e:
        logger.error(f"Docker 상태 조회 실패: {str(e)}")
        return {
            "success": False,
            "containers": [],
            "total": 0,
            "error": str(e)
        }


def run_full_scan(fast_mode: bool = True, enable_poc: bool = True, enable_cce: bool = False) -> Dict[str, Any]:
    """
    전체 스캔 실행 (CVE-Lab 대상)
    
    Args:
        fast_mode: 빠른 스캔 모드 (기본값: True)
        enable_poc: PoC 재현 활성화 (기본값: True)
        enable_cce: CCE 점검 활성화 (기본값: False, Agent에서 호출 시 별도로 실행)
    
    Returns:
        스캔 결과 딕셔너리
    """
    try:
        # 동적 import로 순환 참조 방지
        from scripts.test.scan_cve_lab_full import CVELabScanner
        
        scanner = CVELabScanner(
            fast_mode=fast_mode,
            enable_poc=enable_poc,
            enable_cce=enable_cce
        )
        
        results = scanner.scan_all(parallel=fast_mode)
        
        return {
            "success": True,
            "results": results
        }
    except Exception as e:
        logger.error(f"전체 스캔 실행 실패: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


def run_cce_check(data_json_path: Optional[str] = None) -> Dict[str, Any]:
    """
    CCE 점검 실행 (모든 Docker 컨테이너 대상)
    
    Args:
        data_json_path: data.json 파일 경로 (기본값: 프로젝트 루트/data.json)
    
    Returns:
        CCE 점검 결과 딕셔너리
    """
    try:
        if data_json_path is None:
            data_json_path = project_root / "data.json"
        
        result = run_cce_checks_for_all_containers(data_json_path)
        
        return result
    except Exception as e:
        logger.error(f"CCE 점검 실행 실패: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

