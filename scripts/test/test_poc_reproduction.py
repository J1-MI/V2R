"""
PoC 재현 기능 테스트 스크립트
Docker 소켓 접근 및 컨테이너 생성 테스트
"""

import sys
import logging
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.poc.isolation import IsolationEnvironment
from src.poc.reproduction import POCReproducer

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_docker_client():
    """Docker 클라이언트 연결 테스트"""
    logger.info("=" * 60)
    logger.info("Docker 클라이언트 연결 테스트")
    logger.info("=" * 60)
    
    try:
        env = IsolationEnvironment()
        logger.info("✓ Docker 클라이언트 초기화 성공")
        
        # Docker 데몬 연결 테스트
        env.client.ping()
        logger.info("✓ Docker 데몬 연결 성공")
        
        # 컨테이너 목록 조회
        containers = env.client.containers.list(all=True, limit=5)
        logger.info(f"✓ 컨테이너 목록 조회 성공: {len(containers)}개")
        
        return True
    except Exception as e:
        logger.error(f"✗ Docker 클라이언트 연결 실패: {str(e)}")
        logger.exception(e)
        return False


def test_container_creation():
    """컨테이너 생성 테스트"""
    logger.info("=" * 60)
    logger.info("컨테이너 생성 테스트")
    logger.info("=" * 60)
    
    try:
        env = IsolationEnvironment()
        container_name = "v2r-test-poc-container"
        
        # 기존 컨테이너 삭제 (있다면)
        try:
            existing = env.client.containers.get(container_name)
            existing.remove(force=True)
            logger.info(f"기존 컨테이너 삭제: {container_name}")
        except:
            pass
        
        # 컨테이너 생성
        container_id = env.create_container(
            name=container_name,
            environment={"TEST": "true"}
        )
        logger.info(f"✓ 컨테이너 생성 성공: {container_id[:12]}")
        
        # 컨테이너 시작
        started = env.start_container()
        if started:
            logger.info("✓ 컨테이너 시작 성공")
        else:
            logger.error("✗ 컨테이너 시작 실패")
            return False
        
        # 컨테이너 정보 조회
        info = env.get_container_info()
        logger.info(f"✓ 컨테이너 정보 조회 성공: {info.get('status')}")
        
        # 정리
        env.cleanup()
        logger.info("✓ 테스트 컨테이너 정리 완료")
        
        return True
    except Exception as e:
        logger.error(f"✗ 컨테이너 생성 실패: {str(e)}")
        logger.exception(e)
        return False


def test_poc_reproduction():
    """PoC 재현 테스트"""
    logger.info("=" * 60)
    logger.info("PoC 재현 테스트")
    logger.info("=" * 60)
    
    try:
        reproducer = POCReproducer()
        
        # 간단한 테스트 PoC 스크립트
        test_poc = """
import sys
print("Test PoC executed successfully")
sys.exit(0)
"""
        
        result = reproducer.reproduce(
            poc_script=test_poc,
            poc_type="test",
            target_host="127.0.0.1",
            network_enabled=False
        )
        
        logger.info(f"PoC 재현 결과: {result.get('status')}")
        execution_result = result.get('execution_result', {})
        logger.info(f"  - Exit code: {execution_result.get('exit_code')}")
        logger.info(f"  - Stdout: {execution_result.get('stdout', '')[:200]}")
        logger.info(f"  - Stderr: {execution_result.get('stderr', '')[:200]}")
        
        if result.get('status') == 'success':
            logger.info("✓ PoC 재현 성공")
            return True
        else:
            error_msg = result.get('error', 'Unknown error')
            logger.error(f"✗ PoC 재현 실패: {error_msg}")
            if execution_result.get('stdout'):
                logger.error(f"  Stdout: {execution_result.get('stdout')}")
            if execution_result.get('stderr'):
                logger.error(f"  Stderr: {execution_result.get('stderr')}")
            return False
            
    except Exception as e:
        logger.error(f"✗ PoC 재현 테스트 실패: {str(e)}")
        logger.exception(e)
        return False


if __name__ == "__main__":
    logger.info("PoC 재현 기능 진단 테스트 시작")
    
    results = []
    
    # 1. Docker 클라이언트 테스트
    results.append(("Docker 클라이언트", test_docker_client()))
    
    # 2. 컨테이너 생성 테스트
    if results[0][1]:  # Docker 클라이언트가 성공한 경우만
        results.append(("컨테이너 생성", test_container_creation()))
        
        # 3. PoC 재현 테스트
        if results[1][1]:  # 컨테이너 생성이 성공한 경우만
            results.append(("PoC 재현", test_poc_reproduction()))
    
    # 결과 요약
    logger.info("=" * 60)
    logger.info("테스트 결과 요약")
    logger.info("=" * 60)
    for name, success in results:
        status = "✓ 통과" if success else "✗ 실패"
        logger.info(f"{name}: {status}")
    
    all_passed = all(r[1] for r in results)
    if all_passed:
        logger.info("모든 테스트 통과!")
    else:
        logger.error("일부 테스트 실패. 위의 에러 메시지를 확인하세요.")

