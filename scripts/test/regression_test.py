#!/usr/bin/env python3
"""
V2R 프로젝트 회귀 테스트 스크립트
정리/리팩터링 후 모든 기능이 정상 동작하는지 확인합니다.
"""

import sys
import os
import time
import requests
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

# 프로젝트 루트 경로 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.database import get_db, initialize_database
from src.database.repository import ScanResultRepository, POCReproductionRepository, CCECheckResultRepository, AgentRepository, AgentTaskRepository

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RegressionTest:
    """회귀 테스트 클래스"""
    
    def __init__(self, api_url: str = "http://localhost:5000"):
        self.api_url = api_url.rstrip("/")
        self.results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
    
    def test(self, name: str, test_func):
        """테스트 실행"""
        self.total_tests += 1
        try:
            result = test_func()
            if result:
                self.passed_tests += 1
                self.results.append(("PASS", name))
                logger.info(f"[PASS] {name}")
            else:
                self.failed_tests += 1
                self.results.append(("FAIL", name, "Test returned False"))
                logger.error(f"[FAIL] {name} - Test returned False")
        except Exception as e:
            self.failed_tests += 1
            self.results.append(("FAIL", name, str(e)))
            logger.error(f"[FAIL] {name} - {str(e)}")
    
    def print_summary(self):
        """테스트 결과 요약 출력"""
        print("\n" + "=" * 60)
        print("회귀 테스트 결과 요약")
        print("=" * 60)
        print(f"총 테스트: {self.total_tests}")
        print(f"성공: {self.passed_tests}")
        print(f"실패: {self.failed_tests}")
        print("\n상세 결과:")
        for status, name, *error in self.results:
            if status == "PASS":
                print(f"  ✅ {name}")
            else:
                error_msg = error[0] if error else "Unknown error"
                print(f"  ❌ {name}: {error_msg}")
        print("=" * 60)
        return self.failed_tests == 0


def test_api_health():
    """API 서버 헬스 체크"""
    try:
        response = requests.get(f"{test_runner.api_url}/api/agents", timeout=5)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"API health check failed: {str(e)}")
        return False


def test_database_connection():
    """데이터베이스 연결 테스트"""
    try:
        from sqlalchemy import text
        db = get_db()
        with db.get_session() as session:
            session.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        return False


def test_agent_registration():
    """Agent 등록 테스트"""
    try:
        import platform
        os_info = {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor()
        }
        
        response = requests.post(
            f"{test_runner.api_url}/api/agents/register",
            json={
                "agent_name": "regression_test_agent",
                "os_info": os_info
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get("success") and "agent_id" in data and "agent_token" in data
        return False
    except Exception as e:
        logger.error(f"Agent registration failed: {str(e)}")
        return False


def test_agent_list():
    """Agent 목록 조회 테스트"""
    try:
        response = requests.get(f"{test_runner.api_url}/api/agents", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get("success") and "agents" in data
        return False
    except Exception as e:
        logger.error(f"Agent list failed: {str(e)}")
        return False


def test_dashboard_data():
    """대시보드 데이터 조회 테스트"""
    try:
        db = get_db()
        with db.get_session() as session:
            scan_repo = ScanResultRepository(session)
            stats = scan_repo.get_statistics()
            
            # 기본 통계 구조 확인
            required_keys = ["total", "by_status", "by_severity", "by_scanner"]
            return all(key in stats for key in required_keys)
    except Exception as e:
        logger.error(f"Dashboard data test failed: {str(e)}")
        return False


def test_scan_result_storage():
    """스캔 결과 저장 테스트"""
    try:
        db = get_db()
        with db.get_session() as session:
            scan_repo = ScanResultRepository(session)
            
            # 테스트 데이터 생성
            from datetime import datetime
            test_data = {
                "scan_id": f"test_scan_{int(time.time())}",
                "target_host": "test.example.com",
                "scan_type": "test",
                "scanner_name": "test_scanner",
                "scan_timestamp": datetime.now(),
                "raw_result": {"test": "data"},
                "normalized_result": {"findings": []},
                "cve_list": [],
                "severity": "Info",
                "status": "completed"
            }
            
            result = scan_repo.save(test_data)
            return result is not None and result.scan_id == test_data["scan_id"]
    except Exception as e:
        logger.error(f"Scan result storage test failed: {str(e)}")
        return False


def test_cce_repository():
    """CCE Repository 테스트"""
    try:
        db = get_db()
        with db.get_session() as session:
            cce_repo = CCECheckResultRepository(session)
            # 최소한 Repository가 초기화되는지 확인
            return cce_repo is not None
    except Exception as e:
        logger.error(f"CCE repository test failed: {str(e)}")
        return False


def test_poc_repository():
    """PoC Repository 테스트"""
    try:
        db = get_db()
        with db.get_session() as session:
            poc_repo = POCReproductionRepository(session)
            # 최소한 Repository가 초기화되는지 확인
            return poc_repo is not None
    except Exception as e:
        logger.error(f"PoC repository test failed: {str(e)}")
        return False


def test_agent_repository():
    """Agent Repository 테스트"""
    try:
        db = get_db()
        with db.get_session() as session:
            agent_repo = AgentRepository(session)
            # 최소한 Repository가 초기화되는지 확인
            return agent_repo is not None
    except Exception as e:
        logger.error(f"Agent repository test failed: {str(e)}")
        return False


def test_agent_task_repository():
    """Agent Task Repository 테스트"""
    try:
        db = get_db()
        with db.get_session() as session:
            task_repo = AgentTaskRepository(session)
            # 최소한 Repository가 초기화되는지 확인
            return task_repo is not None
    except Exception as e:
        logger.error(f"Agent task repository test failed: {str(e)}")
        return False


def test_scanner_modules():
    """스캐너 모듈 import 테스트"""
    try:
        from src.scanner import NmapScanner, NucleiScanner, ScanResultNormalizer
        from src.scanner.docker_lab import get_docker_status, run_full_scan, run_cce_check
        return True
    except Exception as e:
        logger.error(f"Scanner modules test failed: {str(e)}")
        return False


def test_pipeline_modules():
    """파이프라인 모듈 import 테스트"""
    try:
        from src.pipeline import ScannerPipeline, POCPipeline
        return True
    except Exception as e:
        logger.error(f"Pipeline modules test failed: {str(e)}")
        return False


def test_llm_module():
    """LLM 모듈 import 테스트"""
    try:
        from src.llm import LLMReportGenerator
        # LLM 초기화 (API 키가 없어도 import는 성공해야 함)
        llm = LLMReportGenerator()
        return True
    except Exception as e:
        logger.error(f"LLM module test failed: {str(e)}")
        return False


def test_report_module():
    """리포트 모듈 import 테스트"""
    try:
        from src.report import ReportGenerator
        return True
    except Exception as e:
        logger.error(f"Report module test failed: {str(e)}")
        return False


def main():
    """메인 테스트 실행"""
    global test_runner
    
    print("=" * 60)
    print("V2R 프로젝트 회귀 테스트")
    print("=" * 60)
    print()
    
    # API URL 확인
    api_url = os.getenv("API_SERVER_URL", "http://localhost:5000")
    print(f"API 서버 URL: {api_url}")
    print()
    
    test_runner = RegressionTest(api_url=api_url)
    
    # 테스트 실행
    print("회귀 테스트 실행 중...\n")
    
    # 1. 기본 연결 테스트
    test_runner.test("API 서버 헬스 체크", test_api_health)
    test_runner.test("데이터베이스 연결", test_database_connection)
    
    # 2. Agent 기능 테스트
    test_runner.test("Agent 등록", test_agent_registration)
    test_runner.test("Agent 목록 조회", test_agent_list)
    
    # 3. Repository 테스트
    test_runner.test("스캔 결과 저장", test_scan_result_storage)
    test_runner.test("CCE Repository", test_cce_repository)
    test_runner.test("PoC Repository", test_poc_repository)
    test_runner.test("Agent Repository", test_agent_repository)
    test_runner.test("Agent Task Repository", test_agent_task_repository)
    
    # 4. 대시보드 데이터 테스트
    test_runner.test("대시보드 데이터 조회", test_dashboard_data)
    
    # 5. 모듈 import 테스트
    test_runner.test("스캐너 모듈", test_scanner_modules)
    test_runner.test("파이프라인 모듈", test_pipeline_modules)
    test_runner.test("LLM 모듈", test_llm_module)
    test_runner.test("리포트 모듈", test_report_module)
    
    # 결과 출력
    success = test_runner.print_summary()
    
    return 0 if success else 1


if __name__ == "__main__":
    import os
    sys.exit(main())

