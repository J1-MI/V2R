"""
PoC 재현 모듈
격리된 환경에서 PoC를 실행하고 결과를 판정합니다.
"""

import logging
import subprocess
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path

from src.poc.isolation import IsolationEnvironment
from src.config import PROJECT_ROOT

logger = logging.getLogger(__name__)


class POCReproducer:
    """PoC 재현 클래스"""

    def __init__(self, base_image: str = "python:3.11-slim"):
        """
        Args:
            base_image: 격리 환경 기본 이미지
        """
        self.base_image = base_image
        self.isolation = None
        self.reproduction_id = None

    def reproduce(
        self,
        poc_script: str,
        poc_type: str = "command_injection",
        target_host: Optional[str] = None,
        timeout: int = 300,
        network_enabled: bool = True
    ) -> Dict[str, Any]:
        """
        PoC 재현 실행

        Args:
            poc_script: PoC 스크립트 내용 또는 파일 경로
            poc_type: PoC 유형 (command_injection, sql_injection, etc.)
            target_host: 대상 호스트 (네트워크 PoC인 경우)
            timeout: 실행 타임아웃 (초)
            network_enabled: 네트워크 활성화 여부

        Returns:
            재현 결과 딕셔너리
        """
        self.reproduction_id = f"poc_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"

        logger.info(f"Starting PoC reproduction: {self.reproduction_id} (type: {poc_type})")

        try:
            # 1. 격리 환경 생성
            self.isolation = IsolationEnvironment(base_image=self.base_image)
            from src.utils.id_generator import generate_container_name
            container_name = generate_container_name("v2r-poc", self.reproduction_id)

            # 환경 변수 설정
            environment = {
                "POC_TYPE": poc_type,
                "TARGET_HOST": target_host or "",
                "REPRODUCTION_ID": self.reproduction_id
            }

            # 컨테이너 생성 및 시작
            self.isolation.create_container(
                name=container_name,
                environment=environment,
                network_disabled=not network_enabled
            )
            self.isolation.start_container()

            # 2. PoC 스크립트 준비
            poc_content = self._prepare_poc_script(poc_script)
            poc_path = f"/tmp/poc_{self.reproduction_id}.py"

            # 스크립트를 로컬에 저장
            local_poc_file = PROJECT_ROOT / "evidence" / f"poc_{self.reproduction_id}.py"
            local_poc_file.parent.mkdir(parents=True, exist_ok=True)
            local_poc_file.write_text(poc_content, encoding="utf-8")

            # 컨테이너에 파일 복사 (Python으로 base64 인코딩하여 전송)
            import base64
            poc_encoded = base64.b64encode(poc_content.encode('utf-8')).decode('utf-8')
            
            # base64 디코딩하여 파일 생성
            create_file_cmd = f"""python3 -c "
import base64
content = base64.b64decode('{poc_encoded}').decode('utf-8')
with open('{poc_path}', 'w') as f:
    f.write(content)
print('File created successfully')
" """
            result = self.isolation.execute_command(create_file_cmd)
            if result["exit_code"] != 0:
                logger.error(f"Failed to create PoC file: {result.get('stdout', '')} {result.get('stderr', '')}")
                raise RuntimeError(f"Failed to create PoC file in container: {result.get('stdout', '')}")

            # 3. PoC 실행
            execution_result = self._execute_poc(poc_path, timeout)
            
            # 실행 결과 로깅
            logger.info(f"PoC execution result: exit_code={execution_result.get('exit_code')}, "
                       f"stdout_length={len(execution_result.get('stdout', ''))}, "
                       f"stderr_length={len(execution_result.get('stderr', ''))}")
            if execution_result.get('stdout'):
                logger.debug(f"PoC stdout: {execution_result.get('stdout')[:200]}")
            if execution_result.get('stderr'):
                logger.warning(f"PoC stderr: {execution_result.get('stderr')[:200]}")

            # 4. 결과 판정
            status = self._determine_status(execution_result, poc_type)

            # 5. 컨테이너 정보 수집
            container_info = self.isolation.get_container_info()

            result = {
                "reproduction_id": self.reproduction_id,
                "poc_type": poc_type,
                "target_host": target_host,
                "status": status,
                "execution_result": execution_result,
                "container_info": container_info,
                "timestamp": datetime.now().isoformat()
            }

            logger.info(f"PoC reproduction completed: {self.reproduction_id} (status: {status})")
            return result

        except Exception as e:
            logger.error(f"PoC reproduction failed: {self.reproduction_id} - {str(e)}")
            return {
                "reproduction_id": self.reproduction_id,
                "poc_type": poc_type,
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def _prepare_poc_script(self, poc_script: str) -> str:
        """
        PoC 스크립트 준비

        Args:
            poc_script: PoC 스크립트 내용 또는 파일 경로

        Returns:
            PoC 스크립트 내용
        """
        # 파일 경로인 경우 읽기
        script_path = Path(poc_script)
        if script_path.exists():
            return script_path.read_text(encoding="utf-8")

        # 이미 스크립트 내용인 경우
        return poc_script

    def _execute_poc(self, poc_path: str, timeout: int) -> Dict[str, Any]:
        """
        PoC 스크립트 실행

        Args:
            poc_path: 컨테이너 내 PoC 스크립트 경로
            timeout: 타임아웃 (초)

        Returns:
            실행 결과
        """
        try:
            # Python 스크립트 실행 (파일이 존재하는지 먼저 확인)
            # shell=True로 실행하여 && 연산자 정상 처리
            check_file_cmd = f"sh -c 'test -f {poc_path} && echo File exists || echo File not found'"
            check_result = self.isolation.execute_command(check_file_cmd)
            logger.debug(f"PoC file check: {check_result.get('stdout', '')}")
            
            # 필요한 Python 모듈 설치 확인 및 설치 (실패해도 경고만 남기고 계속 진행)
            install_deps_cmd = "sh -c 'python3 -c \"import requests\" 2>&1 || pip3 install requests --quiet 2>&1 || echo \"Warning: requests not available\"'"
            deps_result = self.isolation.execute_command(install_deps_cmd)
            if deps_result.get('exit_code') != 0:
                logger.warning(f"Dependencies check: {deps_result.get('stdout', '')[:100]}")
            else:
                logger.debug(f"Dependencies check: {deps_result.get('stdout', '')[:100]}")
            
            # Python 스크립트 실행 (단순 파일 실행, -m 옵션 없음)
            result = self.isolation.execute_command(
                f"python3 {poc_path}",
                timeout=timeout
            )

            return {
                "exit_code": result["exit_code"],
                "stdout": result["stdout"],
                "stderr": result["stderr"],
                "success": result["exit_code"] == 0
            }

        except Exception as e:
            logger.error(f"Failed to execute PoC: {str(e)}")
            return {
                "exit_code": -1,
                "stdout": "",
                "stderr": str(e),
                "success": False
            }

    def _determine_status(
        self,
        execution_result: Dict[str, Any],
        poc_type: str
    ) -> str:
        """
        재현 결과 상태 판정

        Args:
            execution_result: 실행 결과
            poc_type: PoC 유형

        Returns:
            상태 (success, failed, partial)
        """
        exit_code = execution_result.get("exit_code", -1)
        stdout = execution_result.get("stdout", "").lower()
        stderr = execution_result.get("stderr", "").lower()
        success = execution_result.get("success", False)
        
        # exit_code가 0이면 성공으로 간주
        # 또는 stdout에 "성공", "success", "완료" 등의 키워드가 있으면 성공으로 간주
        success_keywords = ["성공", "success", "완료", "전송", "executed", "completed"]
        has_success_keyword = any(keyword in stdout for keyword in success_keywords)
        
        if exit_code == 0 or success or has_success_keyword:
            # PoC 유형별 성공 지표 (선택사항)
            success_indicators = {
                "command_injection": ["command", "executed", "output"],
                "sql_injection": ["sql", "query", "result"],
                "rce": ["remote", "code", "execution"],
                "xss": ["script", "alert", "xss"],
                "test": ["test", "success", "executed"]  # 테스트용
            }

            indicators = success_indicators.get(poc_type, [])
            has_indicator = any(ind in stdout or ind in stderr for ind in indicators)

            # exit_code가 0이거나 성공 지표가 있으면 성공
            if exit_code == 0 or has_indicator:
                return "success"
            else:
                return "partial"
        
        # exit_code가 0이 아니면 실패
        logger.warning(f"PoC execution failed: exit_code={exit_code}, stdout={stdout[:100]}, stderr={stderr[:100]}")
        return "failed"

    def create_snapshot(self, tag: Optional[str] = None) -> Optional[str]:
        """
        현재 상태 스냅샷 생성

        Args:
            tag: 스냅샷 태그

        Returns:
            스냅샷 태그
        """
        if self.isolation is None:
            logger.error("Isolation environment not initialized")
            return None

        return self.isolation.create_snapshot(tag)

    def cleanup(self):
        """리소스 정리"""
        if self.isolation:
            self.isolation.cleanup()
            self.isolation = None

