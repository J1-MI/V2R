#!/usr/bin/env python3
"""
CCE (Common Configuration Enumeration) 점검 스크립트
금융보안원 기준 Linux 서버 보안 설정 점검
"""

import sys
import json
import argparse
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

# 프로젝트 루트 경로 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CCEChecker:
    """CCE 점검 클래스"""
    
    def __init__(self, target_host: str = "localhost"):
        """
        Args:
            target_host: 점검 대상 호스트
        """
        self.target_host = target_host
        self.checks = []
        
    def check_ssh_password_auth(self) -> Dict[str, Any]:
        """CCE-LNX-001: SSH 패스워드 인증 설정 점검"""
        try:
            import subprocess
            result = subprocess.run(
                ["grep", "-i", "^PasswordAuthentication", "/etc/ssh/sshd_config"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                value = result.stdout.strip().split()[-1].lower()
                status = "양호" if value == "no" else "취약"
                detail = f"sshd_config: PasswordAuthentication {value}"
            else:
                status = "주의"
                detail = "sshd_config 파일을 읽을 수 없음"
                
            return {
                "id": "CCE-LNX-001",
                "title": "SSH 패스워드 인증 설정",
                "result": status,
                "detail": detail
            }
        except Exception as e:
            logger.error(f"SSH 패스워드 인증 점검 실패: {e}")
            return {
                "id": "CCE-LNX-001",
                "title": "SSH 패스워드 인증 설정",
                "result": "오류",
                "detail": str(e)
            }
    
    def check_root_login(self) -> Dict[str, Any]:
        """CCE-LNX-002: Root 원격 로그인 설정 점검"""
        try:
            import subprocess
            result = subprocess.run(
                ["grep", "-i", "^PermitRootLogin", "/etc/ssh/sshd_config"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                value = result.stdout.strip().split()[-1].lower()
                status = "양호" if value == "no" else "취약"
                detail = f"sshd_config: PermitRootLogin {value}"
            else:
                status = "주의"
                detail = "sshd_config 파일을 읽을 수 없음"
                
            return {
                "id": "CCE-LNX-002",
                "title": "Root 원격 로그인 설정",
                "result": status,
                "detail": detail
            }
        except Exception as e:
            logger.error(f"Root 로그인 점검 실패: {e}")
            return {
                "id": "CCE-LNX-002",
                "title": "Root 원격 로그인 설정",
                "result": "오류",
                "detail": str(e)
            }
    
    def run_all_checks(self) -> List[Dict[str, Any]]:
        """모든 점검 항목 실행"""
        logger.info(f"CCE 점검 시작: {self.target_host}")
        
        checks = [
            self.check_ssh_password_auth(),
            self.check_root_login(),
            # 추가 점검 항목은 여기에 추가
        ]
        
        self.checks = checks
        return checks
    
    def generate_report(self, output_path: str = None) -> Dict[str, Any]:
        """점검 결과 리포트 생성"""
        if not self.checks:
            self.run_all_checks()
        
        total = len(self.checks)
        pass_count = sum(1 for c in self.checks if c["result"] == "양호")
        fail_count = sum(1 for c in self.checks if c["result"] == "취약")
        warn_count = sum(1 for c in self.checks if c["result"] in ["주의", "오류"])
        
        report = {
            "host": self.target_host,
            "checks": self.checks,
            "summary": {
                "total": total,
                "pass": pass_count,
                "fail": fail_count,
                "warn": warn_count,
                "timestamp": datetime.now().isoformat()
            }
        }
        
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            logger.info(f"리포트 저장: {output_path}")
        
        return report


def main():
    parser = argparse.ArgumentParser(description="CCE 점검 스크립트")
    parser.add_argument(
        "--target",
        default="localhost",
        help="점검 대상 호스트 (기본값: localhost)"
    )
    parser.add_argument(
        "--output",
        help="결과 출력 파일 경로 (JSON)"
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="데모 모드 (간단한 출력)"
    )
    
    args = parser.parse_args()
    
    checker = CCEChecker(target_host=args.target)
    report = checker.generate_report(output_path=args.output)
    
    if args.demo:
        print("\n" + "=" * 60)
        print("CCE 점검 데모 결과")
        print("=" * 60)
        print(f"호스트: {report['host']}")
        print(f"총 점검 항목: {report['summary']['total']}")
        print(f"양호: {report['summary']['pass']}")
        print(f"취약: {report['summary']['fail']}")
        print(f"주의: {report['summary']['warn']}")
        print("\n점검 항목:")
        for check in report['checks']:
            status_icon = "✅" if check['result'] == "양호" else "❌" if check['result'] == "취약" else "⚠️"
            print(f"  {status_icon} {check['id']}: {check['title']} - {check['result']}")
    else:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    
    return 0 if report['summary']['fail'] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())



