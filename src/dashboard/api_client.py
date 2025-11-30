"""
API 클라이언트
Flask API 서버와 통신하는 클라이언트 함수
"""

import requests
from typing import Dict, Any, List, Optional
import logging

from src.config import API_SERVER_URL

logger = logging.getLogger(__name__)

# API 서버 기본 URL (trailing slash 제거)
BASE_URL = API_SERVER_URL.rstrip("/")


def get_agents() -> List[Dict[str, Any]]:
    """
    Agent 목록 조회
    
    Returns:
        Agent 리스트
    """
    try:
        url = f"{BASE_URL}/api/agents"
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # HTTP 에러 시 예외 발생
        
        data = response.json()
        if data.get("success"):
            return data.get("agents", [])
        else:
            logger.error(f"Agent 목록 조회 실패: {data.get('error', 'Unknown error')}")
            return []
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Agent 목록 조회 중 네트워크 오류: {str(e)}")
        return []
    except Exception as e:
        logger.error(f"Agent 목록 조회 중 오류: {str(e)}")
        return []


def create_task(agent_id: str, task_type: str, parameters: Optional[Dict[str, Any]] = None) -> Optional[str]:
    """
    Agent에게 작업 생성
    
    Args:
        agent_id: Agent ID
        task_type: 작업 타입 (DOCKER_STATUS, FULL_SCAN, CCE_CHECK, DB_INIT)
        parameters: 작업 파라미터
    
    Returns:
        task_id (성공 시) 또는 None
    """
    try:
        url = f"{BASE_URL}/api/agents/{agent_id}/tasks"
        payload = {
            "task_type": task_type,
            "parameters": parameters or {}
        }
        
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()  # HTTP 에러 시 예외 발생
        
        data = response.json()
        if data.get("success"):
            return data.get("task_id")
        else:
            logger.error(f"작업 생성 실패: {data.get('error', 'Unknown error')}")
            return None
    
    except requests.exceptions.RequestException as e:
        logger.error(f"작업 생성 중 네트워크 오류: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"작업 생성 중 오류: {str(e)}")
        return None


def get_agent_tasks(agent_id: str, status: str = "all") -> List[Dict[str, Any]]:
    """
    Agent 작업 목록 조회
    
    Args:
        agent_id: Agent ID
        status: 작업 상태 (pending, running, completed, failed, all)
    
    Returns:
        작업 리스트
    """
    try:
        url = f"{BASE_URL}/api/agents/{agent_id}/tasks?status={status}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # HTTP 에러 시 예외 발생
        
        data = response.json()
        if data.get("success"):
            return data.get("tasks", [])
        else:
            logger.error(f"작업 목록 조회 실패: {data.get('error', 'Unknown error')}")
            return []
    
    except requests.exceptions.RequestException as e:
        logger.error(f"작업 목록 조회 중 네트워크 오류: {str(e)}")
        return []
    except Exception as e:
        logger.error(f"작업 목록 조회 중 오류: {str(e)}")
        return []

