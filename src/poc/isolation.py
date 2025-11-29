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

    def __init__(self, base_image: str = "python:3.11-slim"):
        """
        Args:
            base_image: 기본 Docker 이미지 (기본값: python:3.11-slim)
        """
        self.base_image = base_image
        self.client = None
        self.container = None
        self.container_id = None
        self.snapshot_tag = None

        try:
            # Docker 클라이언트 초기화 (여러 방법 시도)
            self.client = self._initialize_docker_client()
            logger.info("Docker client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Docker client: {str(e)}")
            logger.warning("PoC 격리 재현 기능은 사용할 수 없습니다. Docker 소켓에 접근할 수 없습니다.")
            raise
    
    def _initialize_docker_client(self):
        """
        Docker 클라이언트 초기화 (Windows/Linux 호환)
        
        Returns:
            Docker 클라이언트 객체
        """
        import os
        import platform
        
        # 방법 1: 환경 변수에서 DOCKER_HOST 확인
        docker_host = os.getenv("DOCKER_HOST")
        
        # 방법 2: 기본 소켓 경로 확인
        socket_paths = [
            "/var/run/docker.sock",  # Linux 표준 경로
            "/run/docker.sock",      # 일부 Linux 배포판
        ]
        
        # Windows Docker Desktop (WSL2)의 경우
        if platform.system() == "Linux":
            # 컨테이너 내부에서 실행 중인 경우
            for socket_path in socket_paths:
                if os.path.exists(socket_path):
                    try:
                        client = docker.DockerClient(base_url=f"unix://{socket_path}")
                        # 연결 테스트
                        client.ping()
                        logger.info(f"Docker client connected via {socket_path}")
                        return client
                    except Exception:
                        continue
        
        # 방법 3: docker.from_env() 사용 (자동 감지)
        try:
            client = docker.from_env()
            # 연결 테스트
            client.ping()
            logger.info("Docker client connected via docker.from_env()")
            return client
        except Exception as e:
            logger.warning(f"docker.from_env() failed: {str(e)}")
        
        # 방법 4: TCP 연결 시도 (Docker Desktop TCP 포트)
        if docker_host and docker_host.startswith("tcp://"):
            try:
                client = docker.DockerClient(base_url=docker_host)
                client.ping()
                logger.info(f"Docker client connected via TCP: {docker_host}")
                return client
            except Exception:
                pass
        
        # 모든 방법 실패
        raise Exception("Cannot connect to Docker daemon. Please check Docker socket access.")

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
            # 참고: containers.create()는 remove 파라미터를 지원하지 않음
            # remove는 containers.run()에서만 사용 가능
            container_config = {
                "image": self.base_image,
                "name": name,
                "detach": True,
                "stdin_open": True,
                "tty": True,
                "volumes": volumes,
                "network_disabled": network_disabled,
                "privileged": privileged
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
        try:
            if self.container is None:
                raise RuntimeError("Container not created or started")

            # exec_run()은 timeout 파라미터를 직접 지원하지 않음
            # 타임아웃이 필요한 경우 signal이나 threading을 사용해야 함
            # 여기서는 workdir만 전달
            exec_result = self.container.exec_run(
                command,
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

