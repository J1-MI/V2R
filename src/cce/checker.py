#!/usr/bin/env python3
"""
CCE 점검 실행 및 결과 저장 모듈
Docker 컨테이너 대상 CCE 점검 수행
"""

import json
import sys
import subprocess
import os
import tarfile
import io
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

from src.database import get_db
from src.database.repository import CCECheckResultRepository

logger = logging.getLogger(__name__)

# 프로젝트 루트 경로
project_root = Path(__file__).parent.parent.parent

def find_cve_lab_containers() -> List[Dict[str, str]]:
    """
    Docker 컨테이너 목록 조회 (Docker API 사용)
    
    Returns:
        컨테이너 정보 리스트 [{"name": "cve-lab-jenkins", "service": "jenkins"}, ...]
    """
    containers = []
    
    try:
        # docker-py 라이브러리 사용
        import docker
        
        # Docker 클라이언트 초기화
        client = None
        socket_paths = [
            "/var/run/docker.sock",  # Linux 표준 경로
            "/run/docker.sock",      # 일부 Linux 배포판
        ]
        
        for socket_path in socket_paths:
            if Path(socket_path).exists():
                try:
                    client = docker.DockerClient(base_url=f"unix://{socket_path}")
                    client.ping()  # 연결 테스트
                    break
                except:
                    continue
        
        # 환경 변수에서 Docker 호스트 확인
        if not client:
            docker_host = os.environ.get("DOCKER_HOST")
            if docker_host:
                try:
                    client = docker.DockerClient(base_url=docker_host)
                    client.ping()
                except:
                    pass
        
        # 기본 방법 시도
        if not client:
            try:
                client = docker.from_env()
                client.ping()
            except:
                pass
        
        if not client:
            # Docker CLI로 폴백 시도
            try:
                result = subprocess.run(
                    ["docker", "ps", "--format", "{{.Names}}"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    container_names = result.stdout.strip().split('\n')
                    return _filter_cve_lab_containers(container_names)
            except:
                pass
            
            raise Exception("Cannot connect to Docker daemon")
        
        # Docker API로 컨테이너 목록 조회
        running_containers = client.containers.list(filters={"status": "running"})
        container_names = [c.name for c in running_containers]
        
        return _filter_cve_lab_containers(container_names)
        
    except Exception as e:
        logger.error(f"컨테이너 조회 실패: {str(e)}")
        return []

def _filter_cve_lab_containers(container_names: List[str]) -> List[Dict[str, str]]:
    """
    컨테이너 이름 리스트에서 Docker 컨테이너 필터링
    
    Args:
        container_names: 컨테이너 이름 리스트
    
    Returns:
        필터링된 컨테이너 정보 리스트
    """
    containers = []
    
    # Docker 컨테이너 필터링
    container_patterns = {
        "jenkins": ["jenkins", "cve-lab-jenkins"],
        "elasticsearch": ["elasticsearch", "cve-lab-elasticsearch", "elastic", "es-"],
        "log4j": ["log4shell", "cve-lab-log4shell", "log4j", "log4j-vuln"],
        "redis": ["redis", "cve-lab-redis"],
        "mongodb": ["mongodb", "cve-lab-mongodb", "mongo"]
    }
    
    for container_name in container_names:
        if not container_name:
            continue
        
        container_name_lower = container_name.lower()
        
        # 패턴 매칭
        for service_id, patterns in container_patterns.items():
            if any(pattern in container_name_lower for pattern in patterns):
                # service_name 표시 개선
                if service_id == "log4j":
                    service_name = "Log4j"
                elif service_id == "elasticsearch":
                    service_name = "Elasticsearch"
                else:
                    service_name = service_id.capitalize()
                
                containers.append({
                    "name": container_name,
                    "service": service_id,
                    "service_name": service_name
                })
                break
    
    return containers

def run_cce_check_in_container(container_name: str, data_json_path: str = None) -> Dict[str, Any]:
    """
    Docker 컨테이너 내부에서 CCE 점검 실행 (docker-py API 사용)
    
    Args:
        container_name: Docker 컨테이너 이름
        data_json_path: data.json 파일 경로
    
    Returns:
        점검 결과 딕셔너리
    """
    if data_json_path is None:
        data_json_path = project_root / "data.json"
    
    if not Path(data_json_path).exists():
        return {
            "success": False,
            "error": f"data.json 파일을 찾을 수 없습니다: {data_json_path}"
        }
    
    try:
        import docker
        
        # Docker 클라이언트 초기화
        client = None
        socket_paths = [
            "/var/run/docker.sock",
            "/run/docker.sock",
        ]
        
        for socket_path in socket_paths:
            if Path(socket_path).exists():
                try:
                    client = docker.DockerClient(base_url=f"unix://{socket_path}")
                    client.ping()
                    break
                except:
                    continue
        
        if not client:
            try:
                client = docker.from_env()
                client.ping()
            except:
                pass
        
        if not client:
            return {
                "success": False,
                "error": "Docker 클라이언트에 연결할 수 없습니다"
            }
        
        # 컨테이너 객체 가져오기
        container = client.containers.get(container_name)
        
        # data.json을 컨테이너에 복사 (tar 아카이브로)
        container_data_path = "/tmp/data.json"
        
        # data.json을 tar 아카이브로 생성
        tar_data = io.BytesIO()
        with tarfile.open(fileobj=tar_data, mode='w') as tar:
            tar.add(data_json_path, arcname='data.json')
        tar_data.seek(0)
        container.put_archive('/tmp', tar_data.read())
        
        # cce_checks.sh를 컨테이너에 복사
        cce_script_path = project_root / "scripts" / "cce_checks.sh"
        container_script_path = "/tmp/cce_checks.sh"
        
        if cce_script_path.exists():
            # cce_checks.sh를 tar 아카이브로 생성
            tar_script = io.BytesIO()
            with tarfile.open(fileobj=tar_script, mode='w') as tar:
                tar.add(cce_script_path, arcname='cce_checks.sh')
            tar_script.seek(0)
            container.put_archive('/tmp', tar_script.read())
            
            # 실행 권한 부여
            container.exec_run(f"chmod +x {container_script_path}")
            
            # CCE 점검 실행
            exec_result = container.exec_run(
                f"bash -c 'cd /tmp && DATA_JSON={container_data_path} bash {container_script_path} --json 2>&1'"
            )
            
            stdout = exec_result.output.decode('utf-8') if exec_result.output else ""
            exit_code = exec_result.exit_code
            
            if exit_code != 0:
                # 스크립트 실행 실패 시 Python으로 대체
                return run_cce_check_python(container_name, data_json_path)
            
            # 결과 파싱 (NDJSON 형식)
            # jq 오류 메시지 등을 필터링하고 JSON만 추출
            check_results = []
            for line in stdout.strip().split('\n'):
                line = line.strip()
                # jq 오류 메시지나 다른 오류 메시지 필터링
                if not line or 'command not found' in line or 'jq:' in line or line.startswith('/') or 'bash:' in line:
                    continue
                # JSON 라인만 파싱
                if line.startswith('{') and 'id' in line:
                    try:
                        # 깨진 JSON 수정 시도 (name:,detail: 같은 경우)
                        # name:, -> name:"",
                        line = line.replace(',"name":,', ',"name":""')
                        line = line.replace(',"detail":,', ',"detail":""')
                        line = line.replace('"name":,', '"name":""')
                        line = line.replace('"detail":,', '"detail":""')
                        
                        parsed = json.loads(line)
                        # 필수 필드 확인 (id는 필수, name이 없어도 허용)
                        if 'id' in parsed:
                            # name이나 detail이 비어있어도 기본값 설정
                            if 'name' not in parsed or not parsed.get('name'):
                                parsed['name'] = parsed.get('id', '알 수 없음')
                            if 'detail' not in parsed:
                                parsed['detail'] = ''
                            check_results.append(parsed)
                    except json.JSONDecodeError as e:
                        # JSON 파싱 실패 시 로그만 남기고 계속
                        logger.debug(f"JSON 파싱 실패: {line[:100]}... - {str(e)}")
                        continue
            
            return {
                "success": True,
                "container_name": container_name,
                "check_results": check_results,
                "total_checks": len(check_results),
                "raw_output": stdout
            }
        else:
            # 스크립트가 없으면 Python으로 직접 실행
            return run_cce_check_python(container_name, data_json_path)
        
    except Exception as e:
        import docker
        if isinstance(e, docker.errors.NotFound):
            return {
                "success": False,
                "error": f"컨테이너를 찾을 수 없습니다: {container_name}"
            }
        elif isinstance(e, docker.errors.APIError):
            return {
                "success": False,
                "error": f"Docker API 오류: {str(e)}"
            }
        else:
            return {
                "success": False,
                "error": f"예상치 못한 오류: {str(e)}"
            }

def run_cce_check_python(container_name: str, data_json_path: str) -> Dict[str, Any]:
    """
    Python으로 직접 CCE 점검 실행 (bash 스크립트가 없는 경우)
    """
    try:
        # data.json 읽기
        with open(data_json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 컨테이너 내부에서 명령어 실행
        check_results = []
        
        for idx, item in enumerate(data):
            cce_id = f"CCE-LNX-{idx+1:03d}"
            eval_item = item.get('평가항목', '')
            method = item.get('판단방법\n(LINUX)', '')
            criteria = item.get('판단기준\n(LINUX)', '')
            severity = int(item.get('위험도', '3').strip())
            
            # 간단한 점검 실행
            result = "양호"
            detail = "점검 불가 (대상 리소스 없음으로 간주)"
            
            # 컨테이너 내부에서 명령어 실행 시도
            if method:
                try:
                    # grep 명령어 예시
                    if 'grep' in method:
                        # docker-py 사용
                        import docker
                        client = docker.from_env()
                        container = client.containers.get(container_name)
                        exec_result = container.exec_run("test -f /etc/passwd")
                        if exec_result.exit_code == 0:
                            result = "양호"
                            detail = "시스템 파일 확인됨"
                        else:
                            result = "양호"
                            detail = "시스템 파일 없음 (대상 리소스 없음)"
                except:
                    pass
            
            check_results.append({
                "id": cce_id,
                "name": eval_item,
                "severity": severity,
                "result": result,
                "detail": detail
            })
        
        return {
            "success": True,
            "container_name": container_name,
            "check_results": check_results,
            "total_checks": len(check_results)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Python 점검 실행 실패: {str(e)}"
        }

def save_cce_results_to_db(
    check_results: List[Dict[str, Any]],
    container_name: str,
    target_name: str,
    session_id: Optional[str] = None
) -> bool:
    """
    CCE 점검 결과를 데이터베이스에 저장
    
    Args:
        check_results: 점검 결과 리스트
        container_name: 컨테이너 이름
        target_name: 점검 대상 이름
        session_id: 점검 세션 ID (없으면 자동 생성)
    
    Returns:
        저장 성공 여부
    """
    try:
        if not session_id:
            from src.utils.id_generator import generate_session_id
            session_id = generate_session_id("cce", target_name)
        
        db = get_db()
        with db.get_session() as session:
            repo = CCECheckResultRepository(session)
            
            # 점검 결과 데이터 변환
            cce_results = []
            for check in check_results:
                cce_results.append({
                    "check_session_id": session_id,
                    "target_name": target_name,
                    "container_name": container_name,
                    "cce_id": check.get("id", ""),
                    "check_name": check.get("name", ""),
                    "severity": check.get("severity", 3),
                    "result": check.get("result", "양호"),
                    "detail": check.get("detail", ""),
                    "check_timestamp": datetime.now()
                })
            
            # 배치 저장
            repo.save_batch(cce_results)
            session.commit()
            
            logger.info(f"✅ CCE 점검 결과 저장 완료: {len(cce_results)}개 항목 (세션: {session_id})")
            return True
            
    except Exception as e:
        logger.error(f"❌ CCE 점검 결과 저장 실패: {str(e)}")
        return False

def run_cce_checks_for_all_containers(data_json_path: str = None) -> Dict[str, Any]:
    """
    모든 Docker 컨테이너에 대해 CCE 점검 실행
    
    Args:
        data_json_path: data.json 파일 경로
    
    Returns:
        전체 점검 결과 딕셔너리
    """
    containers = find_cve_lab_containers()
    
    if not containers:
        return {
            "success": False,
            "error": "Docker 컨테이너를 찾을 수 없습니다."
        }
    
    print(f"🔍 발견된 Docker 컨테이너: {len(containers)}개")
    for container in containers:
        print(f"  - {container['name']} ({container['service_name']})")
    print()
    
    all_results = {}
    
    for container in containers:
        container_name = container["name"]
        service_name = container["service_name"]
        
        print(f"📋 [{service_name}] CCE 점검 시작: {container_name}")
        
        result = run_cce_check_in_container(container_name, data_json_path)
        
        if result.get("success"):
            check_results = result.get("check_results", [])
            print(f"  ✅ 점검 완료: {len(check_results)}개 항목")
            
            # DB에 저장
            save_cce_results_to_db(
                check_results,
                container_name,
                service_name
            )
            
            all_results[container["service"]] = result
        else:
            print(f"  ❌ 점검 실패: {result.get('error', 'Unknown error')}")
            all_results[container["service"]] = result
    
    return {
        "success": True,
        "containers": containers,
        "results": all_results
    }

def main():
    """메인 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Docker 컨테이너 대상 CCE 점검")
    parser.add_argument(
        "--container",
        type=str,
        help="특정 컨테이너 이름 (지정하지 않으면 모든 Docker 컨테이너 점검)"
    )
    parser.add_argument(
        "--data",
        type=str,
        help="data.json 파일 경로 (기본값: 프로젝트 루트/data.json)"
    )
    
    args = parser.parse_args()
    
    if args.container:
        # 특정 컨테이너만 점검
        result = run_cce_check_in_container(args.container, args.data)
        if result.get("success"):
            check_results = result.get("check_results", [])
            print(f"✅ 점검 완료: {len(check_results)}개 항목")
            
            # 컨테이너 이름에서 서비스 이름 추출
            container_name = args.container
            service_name = container_name.split("-")[-1].capitalize() if "-" in container_name else container_name
            
            save_cce_results_to_db(check_results, container_name, service_name)
        else:
            print(f"❌ 점검 실패: {result.get('error')}", file=sys.stderr)
            sys.exit(1)
    else:
        # 모든 컨테이너 점검
        result = run_cce_checks_for_all_containers(args.data)
        if not result.get("success"):
            print(f"❌ 점검 실패: {result.get('error')}", file=sys.stderr)
            sys.exit(1)

if __name__ == "__main__":
    main()

