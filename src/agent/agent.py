"""
Agent 메인 클래스
EC2 서버와 통신하여 작업을 받고 실행
"""

import logging
import time
import requests
from typing import Optional, Dict, Any
from datetime import datetime

from src.agent.config import AGENT_SERVER_URL, AGENT_NAME, POLLING_INTERVAL, TASK_TIMEOUT
from src.agent.task_executor import execute_task
from src.agent.storage import load_config, save_config

logger = logging.getLogger(__name__)


class Agent:
    """Agent 클래스"""
    
    def __init__(self, server_url: Optional[str] = None, agent_name: Optional[str] = None):
        """
        Args:
            server_url: EC2 서버 URL (기본값: config에서 읽음)
            agent_name: Agent 이름 (기본값: config에서 읽음)
        """
        self.server_url = server_url or AGENT_SERVER_URL
        self.agent_name = agent_name or AGENT_NAME
        self.agent_id: Optional[str] = None
        self.agent_token: Optional[str] = None
        self.running = False
        
        if not self.server_url:
            raise ValueError("서버 URL이 설정되지 않았습니다. AGENT_SERVER_URL 환경 변수를 설정하세요.")
        
        # 저장된 설정에서 토큰 로드
        self._load_saved_config()
    
    def _load_saved_config(self) -> None:
        """
        저장된 설정 파일에서 Agent 정보 로드
        """
        config = load_config()
        
        if config:
            saved_agent_id = config.get("agent_id")
            saved_token = config.get("agent_token")
            saved_name = config.get("agent_name")
            saved_server_url = config.get("server_url")
            
            # 서버 URL이 일치하는 경우에만 로드
            if saved_server_url == self.server_url and saved_agent_id and saved_token:
                self.agent_id = saved_agent_id
                self.agent_token = saved_token
                if saved_name:
                    self.agent_name = saved_name
                logger.info(f"저장된 설정 로드 완료: {self.agent_id[:20]}...")
            else:
                logger.info("저장된 설정이 서버 URL과 일치하지 않거나 불완전합니다. 새로 등록합니다.")
    
    def register(self) -> bool:
        """
        EC2 서버에 Agent 등록
        
        Returns:
            등록 성공 여부
        """
        try:
            import platform
            
            # OS 정보 수집
            os_info = {
                "system": platform.system(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor()
            }
            
            url = f"{self.server_url}/api/agents/register"
            payload = {
                "agent_name": self.agent_name,
                "os_info": os_info
            }
            
            logger.info(f"Agent 등록 시도: {self.agent_name}")
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 201:
                data = response.json()
                self.agent_id = data.get("agent_id")
                self.agent_token = data.get("agent_token")
                
                # 설정 파일에 저장
                save_config(
                    agent_id=self.agent_id,
                    agent_token=self.agent_token,
                    agent_name=self.agent_name,
                    server_url=self.server_url
                )
                
                logger.info(f"✅ Agent 등록 완료: {self.agent_id}")
                logger.info(f"✅ 설정 파일에 저장 완료: ~/.v2r_agent/config.json")
                logger.warning(f"⚠️  토큰을 안전하게 보관하세요: {self.agent_token[:20]}...")
                
                return True
            else:
                logger.error(f"❌ Agent 등록 실패: {response.status_code} - {response.text}")
                return False
        
        except Exception as e:
            logger.error(f"❌ Agent 등록 중 오류: {str(e)}")
            return False
    
    def get_tasks(self) -> list:
        """
        대기 중인 작업 조회
        
        Returns:
            작업 리스트
        """
        try:
            url = f"{self.server_url}/api/agents/{self.agent_id}/tasks?status=pending"
            headers = {
                "Authorization": f"Bearer {self.agent_token}"
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return data.get("tasks", [])
            elif response.status_code == 401:
                # 토큰이 유효하지 않음 - 재등록 필요
                logger.warning("토큰이 유효하지 않습니다. 재등록합니다.")
                self.agent_id = None
                self.agent_token = None
                if not self.register():
                    logger.error("재등록 실패")
                return []
            else:
                logger.error(f"작업 조회 실패: {response.status_code} - {response.text}")
                return []
        
        except Exception as e:
            logger.error(f"작업 조회 중 오류: {str(e)}")
            return []
    
    def update_task_status(self, task_id: str, status: str, result: Dict[str, Any]) -> bool:
        """
        작업 상태 업데이트
        
        Args:
            task_id: 작업 ID
            status: 상태 (completed, failed)
            result: 작업 결과
        
        Returns:
            업데이트 성공 여부
        """
        try:
            url = f"{self.server_url}/api/agents/{self.agent_id}/results"
            headers = {
                "Authorization": f"Bearer {self.agent_token}",
                "Content-Type": "application/json"
            }
            payload = {
                "task_id": task_id,
                "status": status,
                "result": result
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                logger.info(f"✅ 작업 결과 업로드 완료: {task_id} ({status})")
                return True
            else:
                logger.error(f"❌ 작업 결과 업로드 실패: {response.status_code} - {response.text}")
                return False
        
        except Exception as e:
            logger.error(f"❌ 작업 결과 업로드 중 오류: {str(e)}")
            return False
    
    def update_task_to_running(self, task_id: str) -> bool:
        """
        작업 상태를 running으로 업데이트
        
        Args:
            task_id: 작업 ID
        
        Returns:
            업데이트 성공 여부
        """
        try:
            url = f"{self.server_url}/api/agents/{self.agent_id}/tasks/{task_id}/status"
            headers = {
                "Authorization": f"Bearer {self.agent_token}",
                "Content-Type": "application/json"
            }
            payload = {
                "status": "running"
            }
            
            response = requests.put(url, json=payload, headers=headers, timeout=10)
            
            if response.status_code == 200:
                logger.info(f"✅ 작업 상태 업데이트: {task_id} -> running")
                return True
            else:
                logger.error(f"❌ 작업 상태 업데이트 실패: {response.status_code} - {response.text}")
                return False
        
        except Exception as e:
            logger.error(f"❌ 작업 상태 업데이트 중 오류: {str(e)}")
            return False
    
    def process_task(self, task: Dict[str, Any]) -> None:
        """
        작업 처리
        
        Args:
            task: 작업 정보
        """
        task_id = task.get("task_id")
        task_type = task.get("task_type")
        parameters = task.get("parameters", {})
        
        logger.info(f"작업 처리 시작: {task_id} ({task_type})")
        
        # 1. 작업 상태를 running으로 업데이트
        self.update_task_to_running(task_id)
        
        # 2. 작업 실행
        execution_result = execute_task(task_type, parameters)
        
        # 3. 결과 업로드 (completed 또는 failed)
        if execution_result.get("success"):
            status = "completed"
        else:
            status = "failed"
        
        self.update_task_status(task_id, status, execution_result)
    
    def run(self) -> None:
        """
        Agent 실행 (폴링 루프)
        """
        # 등록 확인 (저장된 토큰이 없거나 유효하지 않은 경우)
        if not self.agent_id or not self.agent_token:
            logger.info("Agent 등록 중...")
            if not self.register():
                logger.error("Agent 등록 실패. 종료합니다.")
                return
        else:
            logger.info(f"저장된 Agent 정보 사용: {self.agent_id[:20]}...")
        
        self.running = True
        logger.info(f"Agent 시작: {self.agent_id}")
        logger.info(f"폴링 간격: {POLLING_INTERVAL}초")
        logger.info(f"서버 URL: {self.server_url}")
        
        try:
            while self.running:
                # 대기 중인 작업 조회
                tasks = self.get_tasks()
                
                if tasks:
                    logger.info(f"대기 중인 작업 {len(tasks)}개 발견")
                    for task in tasks:
                        self.process_task(task)
                else:
                    logger.debug("대기 중인 작업 없음")
                
                # 폴링 간격만큼 대기
                time.sleep(POLLING_INTERVAL)
        
        except KeyboardInterrupt:
            logger.info("Agent 종료 요청 받음")
            self.running = False
        except Exception as e:
            logger.error(f"Agent 실행 중 오류: {str(e)}")
            self.running = False
    
    def stop(self) -> None:
        """Agent 중지"""
        self.running = False
        logger.info("Agent 중지")

