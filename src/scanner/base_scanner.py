"""
기본 스캐너 추상 클래스
모든 스캐너가 구현해야 하는 인터페이스를 정의합니다.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime


class BaseScanner(ABC):
    """스캐너 기본 클래스"""

    def __init__(self, name: str, timeout: int = 300):
        """
        Args:
            name: 스캐너 이름
            timeout: 기본 타임아웃 (초)
        """
        self.name = name
        self.timeout = timeout
        self.scan_id = None
        self.target = None

    @abstractmethod
    def scan(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        스캔 실행 (추상 메서드)

        Args:
            target: 스캔 대상
            **kwargs: 스캐너별 추가 옵션

        Returns:
            스캔 결과 딕셔너리
        """
        pass

    def _generate_scan_id(self, target: str) -> str:
        """스캔 ID 생성"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_target = target.replace("://", "_").replace("/", "_").replace(".", "_")
        return f"{self.name}_{safe_target}_{timestamp}"

    def validate_target(self, target: str) -> bool:
        """
        스캔 대상 유효성 검사

        Args:
            target: 스캔 대상

        Returns:
            유효성 여부
        """
        if not target or not isinstance(target, str):
            return False

        # 기본 검증: 비어있지 않은 문자열
        return len(target.strip()) > 0

    def get_scanner_info(self) -> Dict[str, Any]:
        """스캐너 정보 반환"""
        return {
            "name": self.name,
            "timeout": self.timeout,
            "version": self.get_version()
        }

    @abstractmethod
    def get_version(self) -> str:
        """스캐너 버전 정보 (추상 메서드)"""
        pass

