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
            container_name = f"v2r-poc-{self.reproduction_id}"

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

            # 스크립트를 컨테이너에 복사
            local_poc_file = PROJECT_ROOT / "evidence" / f"poc_{self.reproduction_id}.py"
            local_poc_file.parent.mkdir(parents=True, exist_ok=True)
            local_poc_file.write_text(poc_content, encoding="utf-8")

            # 컨테이너에 복사 (간단한 방법: exec로 파일 생성)
            self.isolation.execute_command(
                f"mkdir -p /tmp && cat > {poc_path} << 'EOFPOC'\n{poc_content}\nEOFPOC"
            )

            # 3. PoC 실행
            execution_result = self._execute_poc(poc_path, timeout)

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
            # Python 스크립트 실행
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
        if execution_result.get("success", False):
            # 성공 판정 기준
            stdout = execution_result.get("stdout", "").lower()
            stderr = execution_result.get("stderr", "").lower()

            # PoC 유형별 성공 지표
            success_indicators = {
                "command_injection": ["command", "executed", "output"],
                "sql_injection": ["sql", "query", "result"],
                "rce": ["remote", "code", "execution"],
                "xss": ["script", "alert", "xss"]
            }

            indicators = success_indicators.get(poc_type, [])
            has_indicator = any(ind in stdout or ind in stderr for ind in indicators)

            if has_indicator or execution_result.get("exit_code") == 0:
                return "success"
            else:
                return "partial"

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

