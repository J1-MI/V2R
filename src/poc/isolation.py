"""
PoC 격리 환경 모듈
Docker 컨테이너를 사용하여 PoC를 격리된 환경에서 실행합니다.
"""

import docker
import logging
import time
import tarfile
import io
from typing import Optional, Dict, Any, List
from pathlib import Path
from datetime import datetime

from src.config import PROJECT_ROOT

logger = logging.getLogger(__name__)


class IsolationEnvironment:
    """Docker 기반 격리 환경 관리 클래스"""

    def __init__(self, base_image: str = "python:3.11-slim", allow_docker_failure: bool = False):
        """
        Args:
            base_image: 기본 Docker 이미지 (기본값: python:3.11-slim)
            allow_docker_failure: Docker 초기화 실패 시 예외를 발생시키지 않고 계속 진행
        """
        self.base_image = base_image
        self.client = None
        self.container = None
        self.container_id = None
        self.snapshot_tag = None
        self.allow_docker_failure = allow_docker_failure

        try:
            self.client = docker.from_env()
            logger.info("Docker client initialized")
        except Exception as e:
            if allow_docker_failure:
                logger.warning(f"Docker client initialization failed (will skip Docker operations): {str(e)}")
                logger.warning("PoC 격리 재현 기능은 사용할 수 없습니다. Docker 소켓에 접근할 수 없습니다.")
            else:
                logger.error(f"Failed to initialize Docker client: {str(e)}")
                raise

    def create_container(
        self,
        name: Optional[str] = None,
        environment: Optional[Dict[str, str]] = None,
        volumes: Optional[Dict[str, Dict[str, str]]] = None,
        network_disabled: bool = False,
        privileged: bool = False
    ) -> str:
        """
        격리된 컨테이너 생성

        Args:
            name: 컨테이너 이름 (None이면 자동 생성)
            environment: 환경 변수 딕셔너리
            volumes: 볼륨 마운트 설정
            network_disabled: 네트워크 비활성화 여부
            privileged: privileged 모드 활성화 여부

        Returns:
            컨테이너 ID
        """
        if self.client is None:
            if self.allow_docker_failure:
                raise RuntimeError("Docker client is not available. PoC 격리 재현 기능을 사용할 수 없습니다.")
            else:
                raise RuntimeError("Docker client is not initialized")
        
        try:
            if name is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                name = f"v2r-poc-{timestamp}"

            # 기본 볼륨 설정 (증거 저장용)
            if volumes is None:
                evidence_dir = PROJECT_ROOT / "evidence"
                evidence_dir.mkdir(exist_ok=True)
                volumes = {
                    str(evidence_dir): {
                        "bind": "/evidence",
                        "mode": "rw"
                    }
                }

            # 컨테이너 생성 옵션
            container_config = {
                "image": self.base_image,
                "name": name,
                "detach": True,
                "stdin_open": True,
                "tty": True,
                "volumes": volumes,
                "network_disabled": network_disabled,
                "privileged": privileged,
                "remove": False  # 수동으로 삭제
            }

            if environment:
                container_config["environment"] = environment

            self.container = self.client.containers.create(**container_config)
            self.container_id = self.container.id

            logger.info(f"Container created: {name} ({self.container_id[:12]})")
            return self.container_id

        except docker.errors.ImageNotFound:
            logger.info(f"Base image not found, pulling: {self.base_image}")
            self.client.images.pull(self.base_image)
            return self.create_container(name, environment, volumes, network_disabled, privileged)
        except Exception as e:
            logger.error(f"Failed to create container: {str(e)}")
            raise

    def start_container(self) -> bool:
        """
        컨테이너 시작

        Returns:
            시작 성공 여부
        """
        if self.client is None:
            logger.warning("Docker client not available")
            return False
            
        try:
            if self.container is None:
                logger.error("Container not created")
                return False

            self.container.start()
            logger.info(f"Container started: {self.container_id[:12]}")
            return True

        except Exception as e:
            logger.error(f"Failed to start container: {str(e)}")
            return False

    def execute_command(
        self,
        command: str,
        timeout: int = 300,
        workdir: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        컨테이너 내에서 명령어 실행

        Args:
            command: 실행할 명령어
            timeout: 타임아웃 (초)
            workdir: 작업 디렉토리

        Returns:
            실행 결과 딕셔너리 (exit_code, stdout, stderr)
        """
        if self.client is None:
            logger.warning("Docker client not available")
            return {
                "exit_code": -1,
                "stdout": "",
                "stderr": "Docker client not available"
            }
            
        try:
            if self.container is None:
                raise RuntimeError("Container not created or started")

            exec_config = {
                "cmd": command,
                "timeout": timeout
            }

            if workdir:
                exec_config["workdir"] = workdir

            exec_result = self.container.exec_run(
                command,
                timeout=timeout,
                workdir=workdir
            )

            result = {
                "exit_code": exec_result.exit_code,
                "stdout": exec_result.output.decode("utf-8", errors="ignore") if exec_result.output else "",
                "stderr": ""  # exec_run은 stdout/stderr를 구분하지 않음
            }

            logger.info(f"Command executed: {command[:50]}... (exit_code: {result['exit_code']})")
            return result

        except Exception as e:
            logger.error(f"Failed to execute command: {str(e)}")
            return {
                "exit_code": -1,
                "stdout": "",
                "stderr": str(e)
            }

    def copy_to_container(self, src_path: str, dst_path: str) -> bool:
        """
        파일을 컨테이너로 복사

        Args:
            src_path: 호스트의 소스 파일 경로
            dst_path: 컨테이너 내 대상 경로

        Returns:
            복사 성공 여부
        """
        if self.client is None:
            logger.warning("Docker client not available")
            return False
            
        try:
            if self.container is None:
                logger.error("Container not created")
                return False

            src = Path(src_path)
            if not src.exists():
                logger.error(f"Source file not found: {src_path}")
                return False

            # Docker API를 사용한 파일 복사
            import tarfile
            import io

            # tar 아카이브 생성
            tar_stream = io.BytesIO()
            with tarfile.open(fileobj=tar_stream, mode='w') as tar:
                tar.add(src, arcname=dst_path.lstrip('/'))

            tar_stream.seek(0)
            self.container.put_archive("/", tar_stream.read())

            logger.info(f"File copied to container: {src_path} -> {dst_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to copy file to container: {str(e)}")
            return False

    def copy_from_container(self, src_path: str, dst_path: str) -> bool:
        """
        컨테이너에서 파일 복사

        Args:
            src_path: 컨테이너 내 소스 파일 경로
            dst_path: 호스트의 대상 파일 경로

        Returns:
            복사 성공 여부
        """
        if self.client is None:
            logger.warning("Docker client not available")
            return False
            
        try:
            if self.container is None:
                logger.error("Container not created")
                return False

            bits, stat = self.container.get_archive(src_path)
            dst = Path(dst_path)
            dst.parent.mkdir(parents=True, exist_ok=True)

            with open(dst, "wb") as f:
                for chunk in bits:
                    f.write(chunk)

            logger.info(f"File copied from container: {src_path} -> {dst_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to copy file from container: {str(e)}")
            return False

    def create_snapshot(self, tag: Optional[str] = None) -> Optional[str]:
        """
        컨테이너 스냅샷 생성 (이미지로 커밋)

        Args:
            tag: 이미지 태그 (None이면 자동 생성)

        Returns:
            생성된 이미지 태그
        """
        if self.client is None:
            logger.warning("Docker client not available")
            return None
            
        try:
            if self.container is None:
                logger.error("Container not created")
                return None

            if tag is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                tag = f"v2r-poc-snapshot:{timestamp}"

            self.container.commit(tag=tag)
            self.snapshot_tag = tag

            logger.info(f"Snapshot created: {tag}")
            return tag

        except Exception as e:
            logger.error(f"Failed to create snapshot: {str(e)}")
            return None

    def stop_container(self) -> bool:
        """
        컨테이너 중지

        Returns:
            중지 성공 여부
        """
        if self.client is None:
            return True  # Docker가 없으면 이미 중지된 것으로 간주
            
        try:
            if self.container is None:
                return True  # 이미 중지됨

            self.container.stop(timeout=10)
            logger.info(f"Container stopped: {self.container_id[:12]}")
            return True

        except Exception as e:
            logger.error(f"Failed to stop container: {str(e)}")
            return False

    def remove_container(self) -> bool:
        """
        컨테이너 삭제

        Returns:
            삭제 성공 여부
        """
        if self.client is None:
            self.container = None
            self.container_id = None
            return True  # Docker가 없으면 이미 삭제된 것으로 간주
            
        try:
            if self.container is None:
                return True  # 이미 삭제됨

            # 먼저 중지
            try:
                self.container.stop(timeout=5)
            except:
                pass

            self.container.remove(force=True)
            logger.info(f"Container removed: {self.container_id[:12]}")
            self.container = None
            self.container_id = None
            return True

        except Exception as e:
            logger.error(f"Failed to remove container: {str(e)}")
            return False

    def get_container_info(self) -> Dict[str, Any]:
        """
        컨테이너 정보 조회

        Returns:
            컨테이너 정보 딕셔너리
        """
        if self.client is None:
            return {"note": "Docker client not available"}
            
        try:
            if self.container is None:
                return {}

            self.container.reload()
            return {
                "id": self.container.id,
                "name": self.container.name,
                "status": self.container.status,
                "image": self.container.image.tags[0] if self.container.image.tags else "",
                "created": self.container.attrs.get("Created", ""),
                "snapshot_tag": self.snapshot_tag
            }

        except Exception as e:
            logger.error(f"Failed to get container info: {str(e)}")
            return {}

    def cleanup(self):
        """리소스 정리 (컨테이너 삭제)"""
        self.remove_container()

