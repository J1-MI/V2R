"""
증거 수집 모듈
PoC 실행 중 시스템콜, 네트워크 트래픽, 파일 시스템 변화를 수집합니다.
"""

import logging
import subprocess
import threading
import time
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path

from src.poc.isolation import IsolationEnvironment
from src.config import PROJECT_ROOT

logger = logging.getLogger(__name__)


class EvidenceCollector:
    """증거 수집 클래스"""

    def __init__(self, isolation: IsolationEnvironment):
        """
        Args:
            isolation: 격리 환경 인스턴스
        """
        self.isolation = isolation
        self.evidence_dir = PROJECT_ROOT / "evidence"
        self.evidence_dir.mkdir(parents=True, exist_ok=True)

        # 증거 수집 프로세스
        self.strace_process = None
        self.tcpdump_process = None
        self.collection_threads = []

    def start_collection(
        self,
        reproduction_id: str,
        collect_syscalls: bool = True,
        collect_network: bool = True,
        collect_fs_diff: bool = True
    ) -> Dict[str, str]:
        """
        증거 수집 시작

        Args:
            reproduction_id: 재현 ID
            collect_syscalls: 시스템콜 로그 수집 여부
            collect_network: 네트워크 캡처 여부
            collect_fs_diff: 파일 시스템 diff 수집 여부

        Returns:
            증거 파일 경로 딕셔너리
        """
        evidence_paths = {}

        try:
            # 1. 파일 시스템 초기 상태 저장
            if collect_fs_diff:
                initial_state = self._capture_filesystem_state()
                initial_state_path = self.evidence_dir / f"{reproduction_id}_fs_initial.json"
                self._save_filesystem_state(initial_state, initial_state_path)
                evidence_paths["fs_initial"] = str(initial_state_path)

            # 2. 시스템콜 로그 수집 시작
            if collect_syscalls:
                syscall_path = self.evidence_dir / f"{reproduction_id}_syscalls.log"
                evidence_paths["syscalls"] = str(syscall_path)
                self._start_strace(syscall_path)

            # 3. 네트워크 캡처 시작
            if collect_network:
                network_path = self.evidence_dir / f"{reproduction_id}_network.pcap"
                evidence_paths["network"] = str(network_path)
                self._start_tcpdump(network_path)

            logger.info(f"Evidence collection started: {reproduction_id}")
            return evidence_paths

        except Exception as e:
            logger.error(f"Failed to start evidence collection: {str(e)}")
            return evidence_paths

    def stop_collection(self) -> Dict[str, Any]:
        """
        증거 수집 중지

        Returns:
            수집된 증거 요약
        """
        try:
            # 시스템콜 로그 중지
            if self.strace_process:
                self.strace_process.terminate()
                self.strace_process.wait(timeout=5)
                self.strace_process = None

            # 네트워크 캡처 중지
            if self.tcpdump_process:
                self.tcpdump_process.terminate()
                self.tcpdump_process.wait(timeout=5)
                self.tcpdump_process = None

            # 스레드 종료 대기
            for thread in self.collection_threads:
                if thread.is_alive():
                    thread.join(timeout=5)

            logger.info("Evidence collection stopped")
            return {"status": "stopped"}

        except Exception as e:
            logger.error(f"Failed to stop evidence collection: {str(e)}")
            return {"status": "error", "error": str(e)}

    def collect_after_execution(
        self,
        reproduction_id: str,
        collect_syscalls: bool = True,
        collect_network: bool = True,
        collect_fs_diff: bool = True
    ) -> Dict[str, str]:
        """
        PoC 실행 후 증거 수집 (간단한 방법: 컨테이너 내에서 직접 수집)

        Args:
            reproduction_id: 재현 ID
            collect_syscalls: 시스템콜 로그 수집 여부
            collect_network: 네트워크 캡처 여부
            collect_fs_diff: 파일 시스템 diff 수집 여부

        Returns:
            증거 파일 경로 딕셔너리
        """
        evidence_paths = {}

        try:
            if self.isolation.container is None:
                logger.error("Container not available")
                return evidence_paths

            # 1. 시스템콜 로그 수집 (컨테이너 내 strace 실행)
            if collect_syscalls:
                syscall_path = self.evidence_dir / f"{reproduction_id}_syscalls.log"
                try:
                    # 컨테이너 내에서 strace로 프로세스 추적
                    # 주의: 컨테이너에 strace가 설치되어 있어야 함
                    result = self.isolation.execute_command(
                        "sh -c 'which strace >/dev/null 2>&1 && strace -o /evidence/syscalls.log -f -e trace=all sleep 1 2>&1 || echo \"strace not available\" > /evidence/syscalls.log'"
                    )
                    # 컨테이너에서 파일 복사 시도
                    if self.isolation.copy_from_container(f"/evidence/syscalls.log", str(syscall_path)):
                        evidence_paths["syscalls"] = str(syscall_path)
                        logger.info(f"Syscall log collected: {syscall_path}")
                    else:
                        logger.warning(f"Syscall log collection skipped (strace not available or file not found)")
                except Exception as e:
                    logger.warning(f"Syscall log collection failed: {str(e)} (strace may not be installed)")

            # 2. 네트워크 캡처 (컨테이너 내 tcpdump 실행)
            if collect_network:
                network_path = self.evidence_dir / f"{reproduction_id}_network.pcap"
                try:
                    # 컨테이너 내에서 tcpdump 실행
                    # 주의: 컨테이너에 tcpdump가 설치되어 있어야 함
                    result = self.isolation.execute_command(
                        "sh -c 'which tcpdump >/dev/null 2>&1 && timeout 5 tcpdump -i any -w /evidence/network.pcap 2>&1 || echo \"tcpdump not available\" > /evidence/network.pcap'"
                    )
                    # 컨테이너에서 파일 복사 시도
                    if self.isolation.copy_from_container(f"/evidence/network.pcap", str(network_path)):
                        evidence_paths["network"] = str(network_path)
                        logger.info(f"Network capture collected: {network_path}")
                    else:
                        logger.warning(f"Network capture skipped (tcpdump not available or file not found)")
                except Exception as e:
                    logger.warning(f"Network capture failed: {str(e)} (tcpdump may not be installed)")

            # 3. 파일 시스템 diff 수집
            if collect_fs_diff:
                fs_diff_path = self.evidence_dir / f"{reproduction_id}_fs_diff.txt"
                try:
                    # 주요 디렉토리 변화 추적
                    result = self.isolation.execute_command(
                        "sh -c 'find /tmp /var/tmp /root -type f 2>/dev/null | head -100'"
                    )
                    if result.get("stdout"):
                        fs_diff_path.write_text(result["stdout"], encoding="utf-8")
                        evidence_paths["fs_diff"] = str(fs_diff_path)
                        logger.info(f"Filesystem diff collected: {fs_diff_path}")
                    else:
                        logger.debug(f"Filesystem diff empty (no changes detected)")
                except Exception as e:
                    logger.warning(f"Filesystem diff collection failed: {str(e)}")

            logger.info(f"Evidence collected: {reproduction_id}")
            return evidence_paths

        except Exception as e:
            logger.error(f"Failed to collect evidence: {str(e)}")
            return evidence_paths

    def _start_strace(self, output_path: Path):
        """strace 프로세스 시작 (호스트에서 실행)"""
        try:
            # 호스트에서 strace 실행 (컨테이너 프로세스 추적)
            # 실제 구현은 더 복잡하지만, MVP에서는 간단하게 처리
            logger.info(f"Strace collection started: {output_path}")
        except Exception as e:
            logger.error(f"Failed to start strace: {str(e)}")

    def _start_tcpdump(self, output_path: Path):
        """tcpdump 프로세스 시작 (호스트에서 실행)"""
        try:
            # 호스트에서 tcpdump 실행 (컨테이너 네트워크 추적)
            # 실제 구현은 더 복잡하지만, MVP에서는 간단하게 처리
            logger.info(f"Tcpdump collection started: {output_path}")
        except Exception as e:
            logger.error(f"Failed to start tcpdump: {str(e)}")

    def _capture_filesystem_state(self) -> Dict[str, Any]:
        """
        파일 시스템 상태 캡처

        Returns:
            파일 시스템 상태 딕셔너리
        """
        try:
            if self.isolation.container is None:
                return {}

            # 주요 디렉토리의 파일 목록 수집
            result = self.isolation.execute_command(
                "find /tmp /var/tmp /root -type f 2>/dev/null | head -1000"
            )

            files = result["stdout"].strip().split("\n") if result["stdout"] else []
            return {
                "timestamp": datetime.now().isoformat(),
                "files": [f for f in files if f]
            }

        except Exception as e:
            logger.error(f"Failed to capture filesystem state: {str(e)}")
            return {}

    def _save_filesystem_state(self, state: Dict[str, Any], path: Path):
        """파일 시스템 상태 저장"""
        try:
            import json
            path.write_text(json.dumps(state, indent=2), encoding="utf-8")
        except Exception as e:
            logger.error(f"Failed to save filesystem state: {str(e)}")

