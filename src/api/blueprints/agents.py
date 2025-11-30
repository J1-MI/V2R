"""
Agent 관리 Blueprint
Agent 등록, 작업 관리, 결과 업로드 API
"""

from flask import Blueprint, request, jsonify
from typing import Dict, Any, Optional
import logging
from datetime import datetime

from src.database import get_db
from src.database.repository import AgentRepository, AgentTaskRepository
from src.utils.id_generator import (
    generate_agent_id,
    generate_agent_token,
    hash_token
)
from src.api.middleware.auth import require_agent_auth

logger = logging.getLogger(__name__)

agents_bp = Blueprint("agents", __name__)


@agents_bp.route("/agents/register", methods=["POST"])
def register_agent():
    """
    Agent 등록
    
    Request Body:
        {
            "agent_name": str,
            "os_info": dict (optional)
        }
    
    Response:
        {
            "success": bool,
            "agent_id": str,
            "agent_token": str,  # 원본 토큰 (한 번만 제공)
            "message": str
        }
    """
    try:
        data = request.get_json()
        
        if not data or "agent_name" not in data:
            return jsonify({
                "success": False,
                "error": "agent_name이 필요합니다."
            }), 400
        
        agent_name = data["agent_name"]
        os_info = data.get("os_info", {})
        
        # Agent ID 및 토큰 생성
        agent_id = generate_agent_id(agent_name)
        agent_token = generate_agent_token()
        agent_token_hash = hash_token(agent_token)
        
        # DB에 저장
        db = get_db()
        with db.get_session() as session:
            repo = AgentRepository(session)
            
            agent_data = {
                "agent_id": agent_id,
                "agent_name": agent_name,
                "agent_token_hash": agent_token_hash,
                "os_info": os_info,
                "status": "online",
                "last_seen": datetime.now()
            }
            
            agent = repo.save(agent_data)
            
            logger.info(f"Agent 등록 완료: {agent_id} ({agent_name})")
            
            return jsonify({
                "success": True,
                "agent_id": agent_id,
                "agent_token": agent_token,  # 원본 토큰 (한 번만 제공)
                "message": "Agent 등록이 완료되었습니다. 토큰을 안전하게 보관하세요."
            }), 201
    
    except Exception as e:
        logger.error(f"Agent 등록 실패: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"Agent 등록 실패: {str(e)}"
        }), 500


@agents_bp.route("/agents", methods=["GET"])
def list_agents():
    """
    Agent 목록 조회 (대시보드용)
    
    Response:
        {
            "success": bool,
            "agents": List[Dict]
        }
    """
    try:
        db = get_db()
        with db.get_session() as session:
            repo = AgentRepository(session)
            agents = repo.get_all()
            
            return jsonify({
                "success": True,
                "agents": [agent.to_dict() for agent in agents]
            }), 200
    
    except Exception as e:
        logger.error(f"Agent 목록 조회 실패: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"Agent 목록 조회 실패: {str(e)}"
        }), 500


@agents_bp.route("/agents/<agent_id>/tasks", methods=["GET"])
@require_agent_auth
def get_agent_tasks(agent_id: str):
    """
    Agent 작업 목록 조회
    
    Query Parameters:
        status: 작업 상태 필터 (pending, running, completed, failed, all)
                기본값: pending
    
    Response:
        {
            "success": bool,
            "tasks": List[Dict]
        }
    """
    try:
        # 인증된 agent_id와 요청된 agent_id 일치 확인
        if request.agent_id != agent_id:
            return jsonify({
                "success": False,
                "error": "권한이 없습니다."
            }), 403
        
        # 상태 필터 파라미터 (기본값: pending)
        status = request.args.get("status", "pending")
        
        db = get_db()
        with db.get_session() as session:
            repo = AgentTaskRepository(session)
            
            if status.lower() == "all":
                tasks = repo.get_by_agent_id(agent_id, status=None)
            else:
                tasks = repo.get_by_agent_id(agent_id, status=status)
            
            return jsonify({
                "success": True,
                "tasks": [task.to_dict() for task in tasks]
            }), 200
    
    except Exception as e:
        logger.error(f"작업 목록 조회 실패: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"작업 목록 조회 실패: {str(e)}"
        }), 500


@agents_bp.route("/agents/<agent_id>/tasks/<task_id>/status", methods=["PUT"])
@require_agent_auth
def update_task_status_to_running(agent_id: str, task_id: str):
    """
    작업 상태를 running으로 업데이트 (작업 시작 시)
    
    Request Body:
        {
            "status": "running"
        }
    
    Response:
        {
            "success": bool,
            "message": str
        }
    """
    try:
        # 인증된 agent_id와 요청된 agent_id 일치 확인
        if request.agent_id != agent_id:
            return jsonify({
                "success": False,
                "error": "권한이 없습니다."
            }), 403
        
        data = request.get_json()
        
        if not data or data.get("status") != "running":
            return jsonify({
                "success": False,
                "error": "status는 'running'이어야 합니다."
            }), 400
        
        db = get_db()
        with db.get_session() as session:
            repo = AgentTaskRepository(session)
            
            # 작업 존재 확인 및 agent_id 일치 확인
            task = repo.get_by_id(task_id)
            if not task:
                return jsonify({
                    "success": False,
                    "error": "작업을 찾을 수 없습니다."
                }), 404
            
            if task.agent_id != agent_id:
                return jsonify({
                    "success": False,
                    "error": "권한이 없습니다."
                }), 403
            
            # pending 상태만 running으로 변경 가능
            if task.status != "pending":
                return jsonify({
                    "success": False,
                    "error": f"작업 상태가 pending이 아닙니다. 현재 상태: {task.status}"
                }), 400
            
            # 작업 상태를 running으로 업데이트
            success = repo.update_status(task_id, "running", None)
            
            if success:
                logger.info(f"작업 상태 업데이트: {task_id} -> running")
                return jsonify({
                    "success": True,
                    "message": "작업 상태가 running으로 업데이트되었습니다."
                }), 200
            else:
                return jsonify({
                    "success": False,
                    "error": "작업 상태 업데이트 실패"
                }), 500
    
    except Exception as e:
        logger.error(f"작업 상태 업데이트 실패: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"작업 상태 업데이트 실패: {str(e)}"
        }), 500


@agents_bp.route("/agents/<agent_id>/results", methods=["POST"])
@require_agent_auth
def upload_task_result(agent_id: str):
    """
    Agent 작업 결과 업로드
    
    Request Body:
        {
            "task_id": str,
            "status": str,  # completed, failed
            "result": dict
        }
    
    Response:
        {
            "success": bool,
            "message": str
        }
    """
    try:
        # 인증된 agent_id와 요청된 agent_id 일치 확인
        if request.agent_id != agent_id:
            return jsonify({
                "success": False,
                "error": "권한이 없습니다."
            }), 403
        
        data = request.get_json()
        
        if not data or "task_id" not in data or "status" not in data:
            return jsonify({
                "success": False,
                "error": "task_id와 status가 필요합니다."
            }), 400
        
        task_id = data["task_id"]
        status = data["status"]
        result = data.get("result", {})
        
        if status not in ["completed", "failed"]:
            return jsonify({
                "success": False,
                "error": "status는 completed 또는 failed여야 합니다."
            }), 400
        
        db = get_db()
        with db.get_session() as session:
            repo = AgentTaskRepository(session)
            
            # 작업 존재 확인 및 agent_id 일치 확인
            task = repo.get_by_id(task_id)
            if not task:
                return jsonify({
                    "success": False,
                    "error": "작업을 찾을 수 없습니다."
                }), 404
            
            if task.agent_id != agent_id:
                return jsonify({
                    "success": False,
                    "error": "권한이 없습니다."
                }), 403
            
            # running 상태만 completed/failed로 변경 가능
            if task.status != "running":
                return jsonify({
                    "success": False,
                    "error": f"작업 상태가 running이 아닙니다. 현재 상태: {task.status}"
                }), 400
            
            # 작업 상태 업데이트
            success = repo.update_status(task_id, status, result)
            
            if success:
                logger.info(f"작업 결과 업로드 완료: {task_id} ({status})")
                return jsonify({
                    "success": True,
                    "message": "작업 결과가 업로드되었습니다."
                }), 200
            else:
                return jsonify({
                    "success": False,
                    "error": "작업 상태 업데이트 실패"
                }), 500
    
    except Exception as e:
        logger.error(f"작업 결과 업로드 실패: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"작업 결과 업로드 실패: {str(e)}"
        }), 500


@agents_bp.route("/agents/<agent_id>/tasks", methods=["POST"])
def create_task(agent_id: str):
    """
    Agent에게 작업 생성 (대시보드용)
    
    Request Body:
        {
            "task_type": str,  # DOCKER_STATUS, FULL_SCAN, CCE_CHECK, DB_INIT
            "parameters": dict (optional)
        }
    
    Response:
        {
            "success": bool,
            "task_id": str,
            "message": str
        }
    """
    try:
        data = request.get_json()
        
        if not data or "task_type" not in data:
            return jsonify({
                "success": False,
                "error": "task_type이 필요합니다."
            }), 400
        
        task_type = data["task_type"]
        parameters = data.get("parameters", {})
        
        if task_type not in ["DOCKER_STATUS", "FULL_SCAN", "CCE_CHECK", "DB_INIT"]:
            return jsonify({
                "success": False,
                "error": "task_type은 DOCKER_STATUS, FULL_SCAN, CCE_CHECK, DB_INIT 중 하나여야 합니다."
            }), 400
        
        # Agent 존재 확인
        db = get_db()
        with db.get_session() as session:
            agent_repo = AgentRepository(session)
            agent = agent_repo.get_by_id(agent_id)
            
            if not agent:
                return jsonify({
                    "success": False,
                    "error": "Agent를 찾을 수 없습니다."
                }), 404
            
            # 작업 ID 생성
            from src.utils.id_generator import generate_scan_id
            task_id = generate_scan_id("task", agent_id)
            
            # 작업 저장
            task_repo = AgentTaskRepository(session)
            task_data = {
                "task_id": task_id,
                "agent_id": agent_id,
                "task_type": task_type,
                "status": "pending",
                "parameters": parameters
            }
            
            task = task_repo.save(task_data)
            
            logger.info(f"작업 생성 완료: {task_id} (Agent: {agent_id}, Type: {task_type})")
            
            return jsonify({
                "success": True,
                "task_id": task_id,
                "message": "작업이 생성되었습니다."
            }), 201
    
    except Exception as e:
        logger.error(f"작업 생성 실패: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"작업 생성 실패: {str(e)}"
        }), 500

