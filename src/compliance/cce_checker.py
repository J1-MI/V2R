"""
CCE 서버 점검 메인 클래스
전자금융기반시설 Linux 서버 점검을 통합 관리합니다.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from .linux_checker import LinuxChecker

logger = logging.getLogger(__name__)


class CCEChecker:
    """CCE 서버 점검 클래스"""

    def __init__(self):
        self.checker = None

    def check_server(
        self,
        host: str,
        username: str = "root",
        password: Optional[str] = None,
        key_file: Optional[str] = None,
        port: int = 22
    ) -> Dict[str, Any]:
        """
        서버 점검 실행

        Args:
            host: 대상 서버 호스트
            username: SSH 사용자명
            password: SSH 비밀번호
            key_file: SSH 키 파일 경로
            port: SSH 포트

        Returns:
            점검 결과 딕셔너리
        """
        logger.info(f"CCE 서버 점검 시작: {host}")

        self.checker = LinuxChecker(host, username, password, key_file, port)
        
        if not self.checker.connect():
            return {
                "success": False,
                "error": "SSH 연결 실패",
                "host": host,
                "timestamp": datetime.now().isoformat()
            }

        try:
            checks = self.checker.run_all_checks()
            
            # 통계 계산
            total = len(checks)
            양호 = sum(1 for c in checks if c.get("status") == "양호")
            취약 = sum(1 for c in checks if c.get("status") == "취약")
            주의 = sum(1 for c in checks if c.get("status") == "주의")

            result = {
                "success": True,
                "host": host,
                "timestamp": datetime.now().isoformat(),
                "standard": "전자금융기반시설 2025년도 서버 Linux 항목",
                "statistics": {
                    "total": total,
                    "양호": 양호,
                    "취약": 취약,
                    "주의": 주의
                },
                "checks": checks
            }

            logger.info(f"CCE 서버 점검 완료: {host} (양호: {양호}, 취약: {취약}, 주의: {주의})")
            return result

        except Exception as e:
            logger.error(f"CCE 서버 점검 실패: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "host": host,
                "timestamp": datetime.now().isoformat()
            }
        finally:
            if self.checker:
                self.checker.close()

