"""
ID 생성 유틸리티
스캔 ID, 세션 ID, 컨테이너 이름 등 고유 식별자 생성
"""

import uuid
import hashlib
from datetime import datetime
from typing import Optional


def sanitize_target_name(target: str) -> str:
    """
    대상 이름을 안전한 문자열로 변환
    
    Args:
        target: 원본 대상 이름
        
    Returns:
        안전한 문자열 (특수문자 제거)
    """
    if not target:
        return ""
    
    # URL, 경로, 특수문자 처리
    safe = target.replace("://", "_").replace("/", "_").replace(".", "_").replace(":", "_")
    # 공백 제거
    safe = safe.replace(" ", "_")
    # 연속된 언더스코어 제거
    while "__" in safe:
        safe = safe.replace("__", "_")
    # 앞뒤 언더스코어 제거
    safe = safe.strip("_")
    
    return safe


def generate_scan_id(scanner_name: str, target: str, suffix: Optional[str] = None) -> str:
    """
    스캔 ID 생성
    
    Args:
        scanner_name: 스캐너 이름 (예: "nmap", "nuclei")
        target: 스캔 대상
        suffix: 추가 접미사 (예: 포트 정보)
        
    Returns:
        고유한 스캔 ID
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]  # 밀리초 3자리
    unique_id = str(uuid.uuid4())[:8]  # UUID 앞 8자리
    safe_target = sanitize_target_name(target)
    
    # 접미사 처리
    if suffix:
        # 접미사가 너무 길면 해시 사용
        if len(suffix) > 20:
            suffix = hashlib.md5(suffix.encode()).hexdigest()[:8]
        else:
            suffix = suffix.replace(",", "_").replace("-", "_").replace(" ", "_")
        return f"{scanner_name}_{safe_target}_{suffix}_{timestamp}_{unique_id}"
    
    return f"{scanner_name}_{safe_target}_{timestamp}_{unique_id}"


def generate_session_id(prefix: str, target_name: Optional[str] = None, 
                       timestamp_format: str = '%Y%m%d_%H%M%S') -> str:
    """
    세션 ID 생성
    
    Args:
        prefix: 세션 접두사 (예: "cce", "poc")
        target_name: 대상 이름 (선택)
        timestamp_format: 타임스탬프 형식
        
    Returns:
        고유한 세션 ID
    """
    timestamp = datetime.now().strftime(timestamp_format)
    
    if target_name:
        safe_name = target_name.lower().replace(" ", "_").replace("-", "_")
        return f"{prefix}_{safe_name}_{timestamp}"
    
    return f"{prefix}_{timestamp}"


def generate_container_name(prefix: str, identifier: str) -> str:
    """
    컨테이너 이름 생성
    
    Args:
        prefix: 컨테이너 접두사 (예: "v2r-poc", "cve-lab")
        identifier: 고유 식별자 (예: reproduction_id, service_name)
        
    Returns:
        안전한 컨테이너 이름
    """
    safe_id = sanitize_target_name(identifier)
    return f"{prefix}-{safe_id}"


def generate_agent_id(agent_name: str) -> str:
    """
    Agent ID 생성
    
    Args:
        agent_name: Agent 이름
        
    Returns:
        고유한 Agent ID
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]
    unique_id = str(uuid.uuid4())[:8]
    safe_name = sanitize_target_name(agent_name)
    return f"agent_{safe_name}_{timestamp}_{unique_id}"


def generate_agent_token() -> str:
    """
    Agent 토큰 생성
    
    Returns:
        고유한 Agent 토큰 (원본)
    """
    return str(uuid.uuid4()) + "-" + str(uuid.uuid4())


def hash_token(token: str) -> str:
    """
    토큰을 SHA256 해시로 변환
    
    Args:
        token: 원본 토큰
        
    Returns:
        해시된 토큰 (SHA256)
    """
    return hashlib.sha256(token.encode()).hexdigest()


def verify_token(token: str, token_hash: str) -> bool:
    """
    토큰 검증
    
    Args:
        token: 원본 토큰
        token_hash: 저장된 해시값
        
    Returns:
        검증 성공 여부
    """
    return hash_token(token) == token_hash
