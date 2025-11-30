"""
인증 미들웨어
Agent 토큰 기반 인증 처리
"""

from functools import wraps
from flask import request, jsonify
from typing import Optional
import logging

from src.database import get_db
from src.database.repository import AgentRepository
from src.utils.id_generator import hash_token

logger = logging.getLogger(__name__)


def get_token_from_header() -> Optional[str]:
    """
    Authorization 헤더에서 토큰 추출
    
    Returns:
        토큰 문자열 또는 None
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return None
    
    # Bearer 토큰 형식 확인
    if auth_header.startswith("Bearer "):
        return auth_header[7:]  # "Bearer " 제거
    
    return None


def verify_agent_token(token: str) -> Optional[str]:
    """
    Agent 토큰 검증
    
    Args:
        token: 원본 토큰
    
    Returns:
        agent_id (검증 성공 시) 또는 None
    """
    try:
        token_hash = hash_token(token)
        
        db = get_db()
        with db.get_session() as session:
            repo = AgentRepository(session)
            agent = repo.get_by_token_hash(token_hash)
            
            if agent:
                # 마지막 접속 시간 업데이트
                repo.update_last_seen(agent.agent_id)
                return agent.agent_id
        
        return None
    except Exception as e:
        logger.error(f"토큰 검증 실패: {str(e)}")
        return None


def require_agent_auth(f):
    """
    Agent 인증 데코레이터
    
    사용 예:
        @agents_bp.route("/tasks")
        @require_agent_auth
        def get_tasks():
            agent_id = request.agent_id  # 데코레이터가 설정
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = get_token_from_header()
        
        if not token:
            return jsonify({
                "success": False,
                "error": "인증 토큰이 필요합니다. Authorization: Bearer <token> 헤더를 포함하세요."
            }), 401
        
        agent_id = verify_agent_token(token)
        
        if not agent_id:
            return jsonify({
                "success": False,
                "error": "유효하지 않은 토큰입니다."
            }), 401
        
        # request 객체에 agent_id 추가
        request.agent_id = agent_id
        
        return f(*args, **kwargs)
    
    return decorated_function

