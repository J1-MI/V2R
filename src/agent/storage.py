"""
Agent 설정 및 토큰 저장 관리
~/.v2r_agent/config.json에 저장
"""

import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


def get_config_dir() -> Path:
    """
    Agent 설정 디렉토리 경로 반환
    
    Returns:
        ~/.v2r_agent/ 경로
    """
    home = Path.home()
    config_dir = home / ".v2r_agent"
    config_dir.mkdir(exist_ok=True, mode=0o700)  # 소유자만 읽기/쓰기 가능
    return config_dir


def get_config_path() -> Path:
    """
    설정 파일 경로 반환
    
    Returns:
        ~/.v2r_agent/config.json 경로
    """
    return get_config_dir() / "config.json"


def load_config() -> Dict[str, Any]:
    """
    설정 파일에서 Agent 정보 로드
    
    Returns:
        설정 딕셔너리
        {
            "agent_id": str,
            "agent_token": str,
            "agent_name": str,
            "server_url": str
        }
    """
    config_path = get_config_path()
    
    if not config_path.exists():
        return {}
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            logger.info(f"설정 파일 로드 완료: {config_path}")
            return config
    except Exception as e:
        logger.error(f"설정 파일 로드 실패: {str(e)}")
        return {}


def save_config(agent_id: str, agent_token: str, agent_name: str, server_url: str) -> bool:
    """
    Agent 정보를 설정 파일에 저장
    
    Args:
        agent_id: Agent ID
        agent_token: Agent 토큰
        agent_name: Agent 이름
        server_url: 서버 URL
    
    Returns:
        저장 성공 여부
    """
    config_path = get_config_path()
    
    try:
        config = {
            "agent_id": agent_id,
            "agent_token": agent_token,
            "agent_name": agent_name,
            "server_url": server_url
        }
        
        # 파일 권한 설정 (소유자만 읽기/쓰기)
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        # 파일 권한 변경 (600: 소유자만 읽기/쓰기)
        config_path.chmod(0o600)
        
        logger.info(f"설정 파일 저장 완료: {config_path}")
        return True
    
    except Exception as e:
        logger.error(f"설정 파일 저장 실패: {str(e)}")
        return False


def clear_config() -> bool:
    """
    설정 파일 삭제
    
    Returns:
        삭제 성공 여부
    """
    config_path = get_config_path()
    
    try:
        if config_path.exists():
            config_path.unlink()
            logger.info(f"설정 파일 삭제 완료: {config_path}")
        return True
    except Exception as e:
        logger.error(f"설정 파일 삭제 실패: {str(e)}")
        return False

