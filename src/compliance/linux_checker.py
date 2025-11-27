"""
Linux 서버 점검 모듈
전자금융기반시설 2025년도 서버 Linux 항목을 점검합니다.
"""

import logging
import subprocess
import paramiko
from typing import Dict, Any, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class LinuxChecker:
    """Linux 서버 점검 클래스"""

    def __init__(self, host: str, username: str = "root", password: Optional[str] = None, 
                 key_file: Optional[str] = None, port: int = 22):
        """
        Args:
            host: 대상 서버 호스트
            username: SSH 사용자명
            password: SSH 비밀번호
            key_file: SSH 키 파일 경로
            port: SSH 포트
        """
        self.host = host
        self.username = username
        self.password = password
        self.key_file = key_file
        self.port = port
        self.ssh_client = None

    def connect(self) -> bool:
        """SSH 연결"""
        try:
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            if self.key_file:
                self.ssh_client.connect(
                    self.host,
                    port=self.port,
                    username=self.username,
                    key_filename=self.key_file
                )
            elif self.password:
                self.ssh_client.connect(
                    self.host,
                    port=self.port,
                    username=self.username,
                    password=self.password
                )
            else:
                logger.error("SSH 인증 정보가 없습니다 (password 또는 key_file 필요)")
                return False
            
            logger.info(f"SSH 연결 성공: {self.host}")
            return True
        except Exception as e:
            logger.error(f"SSH 연결 실패: {str(e)}")
            return False

    def execute_command(self, command: str) -> Dict[str, Any]:
        """원격 명령어 실행"""
        if not self.ssh_client:
            if not self.connect():
                return {"success": False, "error": "SSH 연결 실패"}
        
        try:
            stdin, stdout, stderr = self.ssh_client.exec_command(command)
            exit_code = stdout.channel.recv_exit_status()
            output = stdout.read().decode('utf-8')
            error = stderr.read().decode('utf-8')
            
            return {
                "success": exit_code == 0,
                "exit_code": exit_code,
                "stdout": output,
                "stderr": error
            }
        except Exception as e:
            logger.error(f"명령어 실행 실패: {str(e)}")
            return {"success": False, "error": str(e)}

    def check_ssh_password_auth(self) -> Dict[str, Any]:
        """
        CCE-LNX-001: SSH PasswordAuthentication 설정 점검
        양호: PasswordAuthentication no
        취약: PasswordAuthentication yes
        """
        result = self.execute_command("grep -E '^PasswordAuthentication' /etc/ssh/sshd_config | awk '{print $2}'")
        
        if not result["success"]:
            return {
                "id": "CCE-LNX-001",
                "title": "SSH PasswordAuthentication 설정",
                "status": "주의",
                "detail": "sshd_config 파일을 읽을 수 없음",
                "recommendation": "SSH 설정 파일 확인 필요"
            }
        
        value = result["stdout"].strip().lower()
        
        if value == "no":
            return {
                "id": "CCE-LNX-001",
                "title": "SSH PasswordAuthentication 설정",
                "status": "양호",
                "detail": f"PasswordAuthentication = {value}",
                "recommendation": "현재 설정 유지"
            }
        else:
            return {
                "id": "CCE-LNX-001",
                "title": "SSH PasswordAuthentication 설정",
                "status": "취약",
                "detail": f"PasswordAuthentication = {value} (권장: no)",
                "recommendation": "PasswordAuthentication을 no로 변경"
            }

    def check_mysql_external_access(self) -> Dict[str, Any]:
        """
        CCE-LNX-002: MySQL 외부 접근 설정 점검
        양호: bind-address = 127.0.0.1 또는 localhost
        취약: bind-address = 0.0.0.0 또는 외부 접근 허용
        """
        result = self.execute_command("grep -E '^bind-address' /etc/mysql/mysql.conf.d/mysqld.cnf /etc/mysql/my.cnf 2>/dev/null | head -1 | awk '{print $NF}'")
        
        if not result["success"] or not result["stdout"].strip():
            # MySQL이 설치되지 않았거나 설정 파일을 찾을 수 없음
            return {
                "id": "CCE-LNX-002",
                "title": "MySQL 외부 접근 설정",
                "status": "주의",
                "detail": "MySQL 설정 파일을 찾을 수 없음",
                "recommendation": "MySQL 설치 여부 확인"
            }
        
        bind_address = result["stdout"].strip()
        
        if bind_address in ["127.0.0.1", "localhost"]:
            return {
                "id": "CCE-LNX-002",
                "title": "MySQL 외부 접근 설정",
                "status": "양호",
                "detail": f"bind-address = {bind_address}",
                "recommendation": "현재 설정 유지"
            }
        else:
            return {
                "id": "CCE-LNX-002",
                "title": "MySQL 외부 접근 설정",
                "status": "취약",
                "detail": f"bind-address = {bind_address} (권장: 127.0.0.1)",
                "recommendation": "bind-address를 127.0.0.1로 변경"
            }

    def check_unnecessary_services(self) -> Dict[str, Any]:
        """
        CCE-LNX-003: 불필요 서비스 실행 여부 점검
        양호: 필수 서비스만 실행
        취약: 불필요한 서비스 실행 중
        """
        result = self.execute_command("systemctl list-units --type=service --state=running --no-pager | grep -E '(telnet|rsh|rlogin|rexec|ftp)' | wc -l")
        
        if not result["success"]:
            return {
                "id": "CCE-LNX-003",
                "title": "불필요 서비스 실행 여부",
                "status": "주의",
                "detail": "서비스 목록을 확인할 수 없음",
                "recommendation": "시스템 서비스 확인 필요"
            }
        
        count = int(result["stdout"].strip() or "0")
        
        if count == 0:
            return {
                "id": "CCE-LNX-003",
                "title": "불필요 서비스 실행 여부",
                "status": "양호",
                "detail": "불필요한 서비스가 실행되지 않음",
                "recommendation": "현재 상태 유지"
            }
        else:
            return {
                "id": "CCE-LNX-003",
                "title": "불필요 서비스 실행 여부",
                "status": "취약",
                "detail": f"불필요한 서비스 {count}개 실행 중",
                "recommendation": "불필요한 서비스 중지 및 비활성화"
            }

    def check_package_updates(self) -> Dict[str, Any]:
        """
        CCE-LNX-004: 패키지 업데이트 상태 점검
        양호: 최신 패키지 또는 최근 업데이트
        취약: 오래된 패키지 또는 보안 업데이트 누락
        """
        result = self.execute_command("apt list --upgradable 2>/dev/null | grep -c upgradable || echo '0'")
        
        if not result["success"]:
            return {
                "id": "CCE-LNX-004",
                "title": "패키지 업데이트 상태",
                "status": "주의",
                "detail": "패키지 목록을 확인할 수 없음",
                "recommendation": "패키지 관리자 확인 필요"
            }
        
        upgradable_count = int(result["stdout"].strip() or "0")
        
        if upgradable_count == 0:
            return {
                "id": "CCE-LNX-004",
                "title": "패키지 업데이트 상태",
                "status": "양호",
                "detail": "모든 패키지가 최신 상태",
                "recommendation": "정기적인 업데이트 유지"
            }
        elif upgradable_count < 10:
            return {
                "id": "CCE-LNX-004",
                "title": "패키지 업데이트 상태",
                "status": "주의",
                "detail": f"업데이트 가능한 패키지 {upgradable_count}개",
                "recommendation": "패키지 업데이트 권장"
            }
        else:
            return {
                "id": "CCE-LNX-004",
                "title": "패키지 업데이트 상태",
                "status": "취약",
                "detail": f"업데이트 가능한 패키지 {upgradable_count}개 (보안 업데이트 필요)",
                "recommendation": "즉시 패키지 업데이트 실행"
            }

    def check_firewall_status(self) -> Dict[str, Any]:
        """
        CCE-LNX-005: 방화벽 상태 점검
        양호: 방화벽 활성화 및 적절한 규칙 설정
        취약: 방화벽 비활성화 또는 규칙 미설정
        """
        # ufw 상태 확인
        result = self.execute_command("ufw status | head -1")
        
        if not result["success"]:
            return {
                "id": "CCE-LNX-005",
                "title": "방화벽 상태",
                "status": "주의",
                "detail": "방화벽 상태를 확인할 수 없음",
                "recommendation": "방화벽 설정 확인 필요"
            }
        
        status = result["stdout"].strip().lower()
        
        if "active" in status:
            return {
                "id": "CCE-LNX-005",
                "title": "방화벽 상태",
                "status": "양호",
                "detail": "방화벽이 활성화되어 있음",
                "recommendation": "현재 설정 유지"
            }
        else:
            return {
                "id": "CCE-LNX-005",
                "title": "방화벽 상태",
                "status": "취약",
                "detail": "방화벽이 비활성화되어 있음",
                "recommendation": "방화벽 활성화 및 규칙 설정"
            }

    def run_all_checks(self) -> List[Dict[str, Any]]:
        """모든 점검 항목 실행"""
        checks = [
            self.check_ssh_password_auth(),
            self.check_mysql_external_access(),
            self.check_unnecessary_services(),
            self.check_package_updates(),
            self.check_firewall_status()
        ]
        
        return checks

    def close(self):
        """SSH 연결 종료"""
        if self.ssh_client:
            self.ssh_client.close()
            logger.info("SSH 연결 종료")

