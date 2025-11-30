"""
Streamlit 대시보드 애플리케이션
취약점 리스트, 신뢰도 점수, 증거 다운로드, 리포트 생성 기능 제공
"""

import streamlit as st
import logging
import pandas as pd
from typing import List, Dict, Any
from pathlib import Path
from datetime import datetime

from src.database import get_db, initialize_database
from src.database.repository import ScanResultRepository, POCReproductionRepository, CCECheckResultRepository
from src.database.models import POCReproduction, POCMetadata, CCECheckResult
from src.report import ReportGenerator
from src.llm import LLMReportGenerator
from src.dashboard.api_client import get_agents, create_task, get_agent_tasks
from sqlalchemy.exc import ProgrammingError
from sqlalchemy import desc

logger = logging.getLogger(__name__)

# 페이지 설정
st.set_page_config(
    page_title="V2R 취약점 진단 대시보드",
    page_icon="🔒",
    layout="wide"
)


def main():
    """메인 대시보드 함수"""
    st.title("🔒 V2R 취약점 진단 대시보드")

    # 사이드바
    with st.sidebar:
        st.header("메뉴")
        page = st.radio(
            "페이지 선택",
            ["Agent & Local Scanner", "대시보드", "취약점 리스트", "PoC 재현 결과", "CCE 점검 결과", "리포트 생성"]
        )

    # 페이지 라우팅
    if page == "Agent & Local Scanner":
        show_agent_control()
    elif page == "대시보드":
        show_dashboard()
    elif page == "취약점 리스트":
        show_vulnerability_list()
    elif page == "PoC 재현 결과":
        show_poc_reproductions()
    elif page == "CCE 점검 결과":
        show_cce_checks()
    elif page == "리포트 생성":
        show_report_generation()


def show_dashboard():
    """대시보드 메인 화면"""
    st.header("📊 대시보드")

    try:
        db = get_db()
        with db.get_session() as session:
            repo = ScanResultRepository(session)

            # 통계 조회
            stats = repo.get_statistics()

            # 통계 표시
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("총 스캔 결과", stats.get("total", 0))

            with col2:
                completed = stats.get("by_status", {}).get("completed", 0)
                st.metric("완료된 스캔", completed)

            with col3:
                critical = stats.get("by_severity", {}).get("Critical", 0)
                st.metric("Critical 취약점", critical)

            with col4:
                high = stats.get("by_severity", {}).get("High", 0)
                st.metric("High 취약점", high)

            # 심각도별 차트
            st.subheader("심각도별 분포")
            severity_data = stats.get("by_severity", {})
            if severity_data:
                severity_df = pd.DataFrame(
                    list(severity_data.items()),
                    columns=["심각도", "건수"]
                )
                st.bar_chart(severity_df.set_index("심각도"))

            # 최근 스캔 결과 (전체 / 최신 그룹 탭 분리)
            st.subheader("최근 스캔 결과")
            recent_scans = repo.get_recent(days=7, limit=100)
            latest_scan_group = repo.get_latest_scan_group()

            tab_all, tab_latest = st.tabs(["📄 전체 최근 스캔", "🕒 가장 최근 스캔 그룹"])

            with tab_all:
                if recent_scans:
                    scan_data = []
                    for scan in recent_scans:
                        # Windows 시스템 시간대 고려하여 표시
                        from datetime import timezone
                        if scan.scan_timestamp.tzinfo is None:
                            # timezone이 없으면 UTC로 가정
                            scan_time = scan.scan_timestamp.replace(tzinfo=timezone.utc)
                        else:
                            scan_time = scan.scan_timestamp
                        
                        scan_data.append({
                            "스캔 ID": (scan.scan_id[:20] + "...") if len(scan.scan_id) > 20 else scan.scan_id,
                            "대상": scan.target_host,
                            "스캐너": scan.scanner_name,
                            "심각도": scan.severity or "Unknown",
                            "상태": scan.status,
                            "스캔 시간": scan_time.strftime("%Y-%m-%d %H:%M:%S")
                        })
                    
                    # 심각도 순으로 정렬
                    severity_order = {"Critical": 5, "High": 4, "Medium": 3, "Low": 2, "Info": 1, "Unknown": 0}
                    scan_df = pd.DataFrame(scan_data)
                    scan_df["심각도_순서"] = scan_df["심각도"].map(severity_order).fillna(0)
                    scan_df = scan_df.sort_values("심각도_순서", ascending=False).drop("심각도_순서", axis=1)
                    
                    st.dataframe(scan_df, width='stretch')
                else:
                    st.info("최근 스캔 결과가 없습니다.")

            with tab_latest:
                if latest_scan_group:
                    st.write(f"**가장 최근 스캔 그룹** (총 {len(latest_scan_group)}건)")
                    scan_data = []
                    for scan in latest_scan_group:
                        from datetime import timezone
                        if scan.scan_timestamp.tzinfo is None:
                            scan_time = scan.scan_timestamp.replace(tzinfo=timezone.utc)
                        else:
                            scan_time = scan.scan_timestamp
                        
                        scan_data.append({
                            "스캔 ID": scan.scan_id,
                            "대상": scan.target_host,
                            "스캐너": scan.scanner_name,
                            "심각도": scan.severity or "Unknown",
                            "상태": scan.status,
                            "스캔 시간": scan_time.strftime("%Y-%m-%d %H:%M:%S")
                        })
                    
                    # 이미 심각도 순으로 정렬되어 있음
                    st.dataframe(pd.DataFrame(scan_data), width='stretch')
                else:
                    st.info("스캔 결과가 아직 없습니다.")

    except ProgrammingError as e:
        if "does not exist" in str(e) or "relation" in str(e).lower():
            st.error("⚠️ 데이터베이스 테이블이 존재하지 않습니다.")
            st.info("데이터베이스를 초기화해야 합니다.")
            if st.button("🔄 데이터베이스 초기화"):
                with st.spinner("데이터베이스 초기화 중..."):
                    try:
                        if initialize_database():
                            st.success("✅ 데이터베이스 초기화 완료! 페이지를 새로고침하세요.")
                            st.rerun()
                        else:
                            st.error("❌ 데이터베이스 초기화 실패")
                    except Exception as init_error:
                        st.error(f"초기화 오류: {str(init_error)}")
            st.code("또는 다음 명령어를 실행하세요:\ndocker exec v2r-app python scripts/utils/reset_db.py", language="bash")
        else:
            st.error(f"대시보드 로드 실패: {str(e)}")
            logger.error(f"Dashboard error: {str(e)}")
    except Exception as e:
        st.error(f"대시보드 로드 실패: {str(e)}")
        logger.error(f"Dashboard error: {str(e)}")


def show_vulnerability_list():
    """취약점 리스트 화면"""
    st.header("📋 취약점 리스트")

    try:
        db = get_db()
        with db.get_session() as session:
            repo = ScanResultRepository(session)

            # 필터 옵션
            col1, col2 = st.columns(2)
            with col1:
                severity_filter = st.selectbox(
                    "심각도 필터",
                    ["전체", "Critical", "High", "Medium", "Low", "Info"]
                )
            with col2:
                scanner_filter = st.selectbox(
                    "스캐너 필터",
                    ["전체", "nmap", "nuclei"]
                )

            # 스캔 결과 조회
            if severity_filter == "전체":
                scans = repo.get_recent(days=30, limit=100)
            else:
                scans = repo.get_by_severity(severity_filter, limit=100)

            if scanner_filter != "전체":
                scans = [s for s in scans if s.scanner_name == scanner_filter]

            # 취약점 데이터 구성
            vulnerabilities = []
            
            # 1. 스캔 결과에서 취약점 추출
            for scan in scans:
                normalized = scan.normalized_result or {}
                findings = normalized.get("findings", [])

                for finding in findings:
                    cve_list = finding.get("cve_list", [])
                    # CVE에 해당하는 PoC 재현 결과의 신뢰도 점수 조회
                    reliability_score = "N/A"
                    if cve_list:
                        try:
                            # 가장 최근의 성공한 PoC 재현 결과의 신뢰도 점수 사용
                            for cve in cve_list[:1]:  # 첫 번째 CVE만 확인
                                poc_meta = session.query(POCMetadata).filter(
                                    POCMetadata.cve_id == cve
                                ).first()
                                if poc_meta:
                                    poc_repro = session.query(POCReproduction).filter(
                                        POCReproduction.poc_id == poc_meta.poc_id,
                                        POCReproduction.status.in_(["success", "partial"])
                                    ).order_by(desc(POCReproduction.reproduction_timestamp)).first()
                                    if poc_repro and poc_repro.reliability_score is not None:
                                        reliability_score = f"{poc_repro.reliability_score}/100"
                                        break
                        except Exception as e:
                            logger.debug(f"Failed to get reliability score for CVE: {str(e)}")
                            reliability_score = "N/A"
                    
                    vulnerabilities.append({
                        "ID": finding.get("finding_id", ""),
                        "제목": finding.get("title", "Unknown"),
                        "심각도": finding.get("severity", "Info"),
                        "CVE": ", ".join(cve_list),
                        "스캐너": scan.scanner_name,
                        "대상": scan.target_host,
                        "발견일": scan.scan_timestamp.strftime("%Y-%m-%d"),
                        "신뢰도": reliability_score
                    })
            
            # 2. PoC 재현 결과에서 취약점 추출 (스캔 결과에 없는 경우)
            try:
                poc_repo = POCReproductionRepository(session)
                
                # 최근 PoC 재현 결과 조회 (LEFT JOIN으로 poc_id가 없는 경우도 포함)
                poc_reproductions = session.query(POCReproduction).outerjoin(
                    POCMetadata, POCReproduction.poc_id == POCMetadata.poc_id
                ).order_by(desc(POCReproduction.reproduction_timestamp)).limit(50).all()
            except Exception as e:
                logger.error(f"Failed to query PoC reproductions: {str(e)}")
                poc_reproductions = []
            
            # 이미 추가된 CVE 추적
            existing_cves = set()
            for vuln in vulnerabilities:
                cves = vuln.get("CVE", "").split(", ")
                existing_cves.update([cve.strip() for cve in cves if cve.strip()])
            
            # PoC 재현 결과에서 새로운 취약점 추가
            for poc in poc_reproductions:
                try:
                    if poc.poc_id:
                        poc_metadata = session.query(POCMetadata).filter(
                            POCMetadata.poc_id == poc.poc_id
                        ).first()
                        
                        if poc_metadata and poc_metadata.cve_id:
                            cve_id = poc_metadata.cve_id
                            # 이미 추가된 CVE는 스킵
                            if cve_id not in existing_cves:
                                existing_cves.add(cve_id)
                                
                                # 상태에 따른 심각도 결정
                                if poc.status == "success":
                                    severity = "High"
                                elif poc.status == "partial":
                                    severity = "Medium"
                                else:
                                    severity = "Low"
                                
                                # 신뢰도 점수 조회 (세션 refresh)
                                session.refresh(poc)
                                reliability_display = "N/A"
                                if poc.reliability_score is not None:
                                    reliability_display = f"{poc.reliability_score}/100"
                                
                                vulnerabilities.append({
                                    "ID": poc.reproduction_id,
                                    "제목": f"{cve_id} (PoC 재현)",
                                    "심각도": severity,
                                    "CVE": cve_id,
                                    "스캐너": "PoC",
                                    "대상": poc.target_host or "Unknown",
                                    "발견일": poc.reproduction_timestamp.strftime("%Y-%m-%d") if poc.reproduction_timestamp else "N/A",
                                    "신뢰도": reliability_display
                                })
                except Exception as e:
                    logger.debug(f"Failed to process PoC reproduction {poc.reproduction_id}: {str(e)}")
                    continue

            if vulnerabilities:
                df = pd.DataFrame(vulnerabilities)
                st.dataframe(df, width='stretch')

                # 증거 다운로드
                st.subheader("증거 다운로드")
                selected_id = st.selectbox("취약점 선택", df["ID"].tolist())

                if st.button("증거 다운로드"):
                    evidence_path = Path("evidence") / f"{selected_id}_*.log"
                    if evidence_path.parent.exists():
                        st.info(f"증거 파일: {evidence_path}")
                    else:
                        st.warning("증거 파일을 찾을 수 없습니다.")
            else:
                st.info("취약점이 없습니다.")

    except ProgrammingError as e:
        if "does not exist" in str(e) or "relation" in str(e).lower():
            st.warning("⚠️ 데이터베이스 테이블이 존재하지 않습니다. 데이터베이스를 초기화하세요.")
            st.info("대시보드 페이지에서 '데이터베이스 초기화' 버튼을 클릭하거나 다음 명령어를 실행하세요:")
            st.code("docker exec v2r-app python scripts/utils/reset_db.py", language="bash")
        else:
            st.error(f"취약점 리스트 로드 실패: {str(e)}")
            logger.error(f"Vulnerability list error: {str(e)}")
    except Exception as e:
        st.error(f"취약점 리스트 로드 실패: {str(e)}")
        logger.error(f"Vulnerability list error: {str(e)}")


def show_poc_reproductions():
    """PoC 재현 결과 화면"""
    st.header("🧪 PoC 재현 결과")

    try:
        db = get_db()
        with db.get_session() as session:
            repo = POCReproductionRepository(session)

            # 상태 필터 옵션
            status_filter = st.selectbox(
                "상태 필터",
                ["전체", "성공", "부분 성공", "실패"],
                key="poc_status_filter"
            )
            
            # 재현 결과 조회 (신뢰도 점수 포함)
            if status_filter == "전체":
                # 모든 상태 조회
                reproductions = session.query(POCReproduction).order_by(
                    desc(POCReproduction.reproduction_timestamp)
                ).limit(100).all()
            elif status_filter == "성공":
                reproductions = session.query(POCReproduction).filter(
                    POCReproduction.status == "success"
                ).order_by(desc(POCReproduction.reproduction_timestamp)).limit(100).all()
            elif status_filter == "부분 성공":
                reproductions = session.query(POCReproduction).filter(
                    POCReproduction.status == "partial"
                ).order_by(desc(POCReproduction.reproduction_timestamp)).limit(100).all()
            else:  # 실패
                reproductions = session.query(POCReproduction).filter(
                    POCReproduction.status == "failed"
                ).order_by(desc(POCReproduction.reproduction_timestamp)).limit(100).all()

            if reproductions:
                poc_data = []
                for poc in reproductions:
                    # 상태에 따른 색상 표시
                    status_display = poc.status
                    if poc.status == "success":
                        status_display = "✅ 성공"
                    elif poc.status == "partial":
                        status_display = "⚠️ 부분 성공"
                    elif poc.status == "failed":
                        status_display = "❌ 실패"
                    else:
                        status_display = f"❓ {poc.status}"
                    
                    # 신뢰도 점수 조회 (세션 refresh)
                    session.refresh(poc)
                    reliability_display = "N/A"
                    if poc.reliability_score is not None:
                        reliability_display = f"{poc.reliability_score}/100"
                    
                    poc_data.append({
                        "재현 ID": poc.reproduction_id,
                        "상태": status_display,
                        "신뢰도 점수": reliability_display,
                        "대상": poc.target_host,
                        "재현 시간": poc.reproduction_timestamp.strftime("%Y-%m-%d %H:%M") if poc.reproduction_timestamp else "N/A"
                    })

                df = pd.DataFrame(poc_data)
                st.dataframe(df, width='stretch')

                # 상세 정보
                if st.checkbox("상세 정보 표시"):
                    selected_ids = [poc.reproduction_id for poc in reproductions]
                    selected_id = st.selectbox("재현 ID 선택", selected_ids)
                    
                    # 선택된 재현의 상세 정보 표시
                    selected_poc = next((p for p in reproductions if p.reproduction_id == selected_id), None)
                    if selected_poc:
                        st.subheader("상세 정보")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**재현 ID**: {selected_poc.reproduction_id}")
                            st.write(f"**상태**: {selected_poc.status}")
                            st.write(f"**대상**: {selected_poc.target_host}")
                            st.write(f"**재현 시간**: {selected_poc.reproduction_timestamp}")
                        with col2:
                            st.write(f"**신뢰도 점수**: {selected_poc.reliability_score or 'N/A'}")
                            st.write(f"**증거 위치**: {selected_poc.evidence_location or 'N/A'}")
                            st.write(f"**시스템콜 로그**: {selected_poc.syscall_log_path or 'N/A'}")
                            st.write(f"**네트워크 캡처**: {selected_poc.network_capture_path or 'N/A'}")
                        
                        # 실패한 경우 오류 정보 표시
                        if selected_poc.status == "failed":
                            st.error("❌ 이 PoC 재현은 실패했습니다.")
                            
                            # 에러 메시지가 evidence_location에 저장되어 있는지 확인
                            if selected_poc.evidence_location and selected_poc.evidence_location.startswith("ERROR:"):
                                error_msg = selected_poc.evidence_location.replace("ERROR: ", "", 1)
                                st.code(error_msg, language="text")
                            
                            # 일반적인 해결 방법 안내
                            with st.expander("🔧 문제 해결 방법"):
                                st.markdown("""
                                **가능한 원인:**
                                1. Docker 소켓 접근 문제
                                2. 컨테이너 생성/실행 실패
                                3. 네트워크 연결 문제
                                4. PoC 스크립트 실행 오류
                                
                                **확인 사항:**
                                - Docker Desktop이 실행 중인지 확인
                                - `docker-compose.yml`에서 Docker 소켓 마운트 확인
                                - 컨테이너 로그 확인: `docker logs <container_id>`
                                """)
            else:
                st.info("PoC 재현 결과가 없습니다.")
                st.info("💡 팁: 스캔 결과에서 CVE를 발견하면 자동으로 PoC 재현이 시도됩니다.")

    except ProgrammingError as e:
        if "does not exist" in str(e) or "relation" in str(e).lower():
            st.warning("⚠️ 데이터베이스 테이블이 존재하지 않습니다. 데이터베이스를 초기화하세요.")
            st.info("대시보드 페이지에서 '데이터베이스 초기화' 버튼을 클릭하거나 다음 명령어를 실행하세요:")
            st.code("docker exec v2r-app python scripts/utils/reset_db.py", language="bash")
        else:
            st.error(f"PoC 재현 결과 로드 실패: {str(e)}")
            logger.error(f"POC reproduction error: {str(e)}")
    except Exception as e:
        st.error(f"PoC 재현 결과 로드 실패: {str(e)}")
        logger.error(f"POC reproduction error: {str(e)}")


def show_cce_checks():
    """CCE 점검 결과 화면"""
    st.header("🛡️ CCE 점검 결과")

    try:
        db = get_db()
        with db.get_session() as session:
            repo = CCECheckResultRepository(session)

            # 최근 점검 세션 목록
            recent_sessions = repo.get_recent_sessions(limit=20)
            latest_session = repo.get_latest_session()

            if not recent_sessions:
                st.info("CCE 점검 결과가 없습니다.")
                st.info("💡 팁: CCE 점검 스크립트를 실행하면 결과가 여기에 표시됩니다.")
                return

            # 세션 정보 조회 (점검 대상 이름 포함)
            session_info_list = []
            for session_id in recent_sessions:
                try:
                    info = repo.get_session_info(session_id)
                    if info:
                        session_info_list.append(info)
                    else:
                        # 세션 정보가 없어도 세션 ID로 표시
                        session_info_list.append({
                            "session_id": session_id,
                            "target_name": session_id.split("_")[1].capitalize() if "_" in session_id else "알 수 없음",
                            "check_timestamp": None,
                            "total_checks": 0
                        })
                except Exception as e:
                    # 세션 정보 조회 실패 시에도 세션 ID만으로 표시
                    logger.warning(f"Failed to get session info for {session_id}: {str(e)}")
                    session_info_list.append({
                        "session_id": session_id,
                        "target_name": session_id.split("_")[1].capitalize() if "_" in session_id else "알 수 없음",
                        "check_timestamp": None,
                        "total_checks": 0
                    })
            
            # 세션 선택 (점검 대상 이름 표시)
            col1, col2 = st.columns([3, 1])
            with col1:
                # 세션 선택 옵션 생성 (점검 대상 이름 포함)
                session_options = []
                for info in session_info_list:
                    target_display = info['target_name'] or "알 수 없음"
                    timestamp = info['check_timestamp'].strftime("%Y-%m-%d %H:%M") if info['check_timestamp'] else ""
                    session_options.append(f"{target_display} ({timestamp})")
                
                if session_options:
                    selected_idx = 0
                    if latest_session:
                        for i, info in enumerate(session_info_list):
                            if info['session_id'] == latest_session:
                                selected_idx = i
                                break
                    
                    selected_display = st.selectbox(
                        "점검 세션 선택",
                        session_options,
                        index=selected_idx,
                        help="같은 실행에서 생성된 점검 결과들을 그룹화한 세션입니다."
                    )
                    # 선택된 세션 ID 찾기
                    selected_idx = session_options.index(selected_display)
                    selected_session = session_info_list[selected_idx]['session_id']
                else:
                    selected_session = recent_sessions[0] if recent_sessions else None
            with col2:
                if st.button("🔄 최신 세션"):
                    selected_session = latest_session
                    st.rerun()
            
            # 선택된 세션의 점검 대상 정보 표시
            if selected_session:
                session_info = repo.get_session_info(selected_session)
                if session_info:
                    st.info(f"**점검 대상**: {session_info['target_name'] or '알 수 없음'} | **점검 시간**: {session_info['check_timestamp'].strftime('%Y-%m-%d %H:%M:%S') if session_info['check_timestamp'] else 'N/A'} | **총 점검 항목**: {session_info['total_checks']}개")

            # 선택된 세션의 점검 결과 조회
            check_results = repo.get_by_session(selected_session)

            if check_results:
                # 통계 표시
                stats = repo.get_statistics(selected_session)
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("총 점검 항목", stats.get("total", 0))
                with col2:
                    양호 = stats.get("by_result", {}).get("양호", 0)
                    st.metric("양호", 양호, delta=None)
                with col3:
                    취약 = stats.get("by_result", {}).get("취약", 0)
                    st.metric("취약", 취약, delta=None, delta_color="inverse")
                with col4:
                    na = stats.get("by_result", {}).get("NOT_APPLICABLE", 0)
                    st.metric("해당 없음", na)

                # 점검 결과 테이블
                st.subheader("점검 결과 상세")
                
                # 필터 옵션
                col1, col2 = st.columns(2)
                with col1:
                    result_filter = st.selectbox(
                        "결과 필터",
                        ["전체", "양호", "취약", "NOT_APPLICABLE"]
                    )
                with col2:
                    severity_filter = st.selectbox(
                        "심각도 필터",
                        ["전체", "5", "4", "3", "2", "1"]
                    )

                # 필터링
                filtered_results = check_results
                if result_filter != "전체":
                    filtered_results = [r for r in filtered_results if r.result == result_filter]
                if severity_filter != "전체":
                    filtered_results = [r for r in filtered_results if r.severity == int(severity_filter)]

                if filtered_results:
                    # 데이터프레임 생성
                    check_data = []
                    for check in filtered_results:
                        check_data.append({
                            "CCE ID": check.cce_id,
                            "평가항목": check.check_name,
                            "심각도": check.severity or "N/A",
                            "결과": check.result,
                            "점검 시간": check.check_timestamp.strftime("%Y-%m-%d %H:%M:%S") if check.check_timestamp else "N/A"
                        })
                    
                    df = pd.DataFrame(check_data)
                    
                    # 심각도 순으로 정렬
                    df["심각도_순서"] = df["심각도"].replace({"N/A": 0}).astype(int)
                    df = df.sort_values("심각도_순서", ascending=False).drop("심각도_순서", axis=1)
                    
                    st.dataframe(df, width='stretch')

                    # 상세 정보
                    if st.checkbox("상세 정보 표시"):
                        selected_cce_id = st.selectbox("CCE ID 선택", df["CCE ID"].tolist())
                        selected_check = next((c for c in filtered_results if c.cce_id == selected_cce_id), None)
                        
                        if selected_check:
                            st.subheader(f"상세 정보: {selected_check.cce_id}")
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write(f"**CCE ID**: {selected_check.cce_id}")
                                st.write(f"**평가항목**: {selected_check.check_name}")
                                st.write(f"**심각도**: {selected_check.severity or 'N/A'}")
                                st.write(f"**결과**: {selected_check.result}")
                            with col2:
                                st.write(f"**점검 시간**: {selected_check.check_timestamp}")
                                st.write(f"**점검 대상**: {selected_check.target_name or '알 수 없음'}")
                                st.write(f"**세션 ID**: {selected_check.check_session_id}")
                            
                            st.subheader("명령 실행 결과")
                            st.code(selected_check.detail or "결과 없음", language="text")
                else:
                    st.info("필터 조건에 맞는 점검 결과가 없습니다.")
            else:
                st.info("선택한 세션에 점검 결과가 없습니다.")

    except ProgrammingError as e:
        if "does not exist" in str(e) or "relation" in str(e).lower():
            st.warning("⚠️ 데이터베이스 테이블이 존재하지 않습니다. 데이터베이스를 초기화하세요.")
            st.info("대시보드 페이지에서 '데이터베이스 초기화' 버튼을 클릭하거나 다음 명령어를 실행하세요:")
            st.code("docker exec v2r-app python scripts/utils/reset_db.py", language="bash")
        else:
            st.error(f"CCE 점검 결과 로드 실패: {str(e)}")
            logger.error(f"CCE check error: {str(e)}")
    except Exception as e:
        st.error(f"CCE 점검 결과 로드 실패: {str(e)}")
        logger.error(f"CCE check error: {str(e)}")


def show_agent_control():
    """Agent & Local Scanner 제어 화면"""
    st.header("🤖 Agent & Local Scanner")
    
    try:
        # Agent 목록 조회
        agents = get_agents()
        
        if not agents:
            st.info("등록된 Agent가 없습니다.")
            st.info("💡 팁: 로컬 PC에서 Agent 프로그램을 실행하면 자동으로 등록됩니다.")
            return
        
        # Agent 목록 표시
        st.subheader("등록된 Agent 목록")
        
        for agent in agents:
            with st.expander(f"🤖 {agent.get('agent_name', 'Unknown')} ({agent.get('agent_id', 'N/A')[:20]}...)"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    status = agent.get("status", "offline")
                    if status == "online":
                        st.success(f"🟢 온라인")
                    else:
                        st.warning(f"🔴 오프라인")
                
                with col2:
                    last_seen = agent.get("last_seen")
                    if last_seen:
                        st.write(f"마지막 접속: {last_seen}")
                    else:
                        st.write("마지막 접속: N/A")
                
                with col3:
                    os_info = agent.get("os_info", {})
                    if os_info:
                        st.write(f"OS: {os_info.get('system', 'Unknown')} {os_info.get('release', '')}")
                
                # 작업 생성 버튼
                st.subheader("작업 생성")
                col1, col2, col3, col4 = st.columns(4)
                
                agent_id = agent.get("agent_id")
                
                with col1:
                    if st.button("Docker 상태 조회", key=f"docker_{agent_id}"):
                        task_id = create_task(agent_id, "DOCKER_STATUS")
                        if task_id:
                            st.success(f"✅ 작업 생성 완료: {task_id}")
                        else:
                            st.error("❌ 작업 생성 실패")
                
                with col2:
                    if st.button("전체 스캔 실행", key=f"full_scan_{agent_id}"):
                        task_id = create_task(agent_id, "FULL_SCAN", {"fast_mode": True, "enable_poc": True, "enable_cce": False})
                        if task_id:
                            st.success(f"✅ 작업 생성 완료: {task_id}")
                        else:
                            st.error("❌ 작업 생성 실패")
                
                with col3:
                    if st.button("CCE 점검 실행", key=f"cce_{agent_id}"):
                        task_id = create_task(agent_id, "CCE_CHECK")
                        if task_id:
                            st.success(f"✅ 작업 생성 완료: {task_id}")
                        else:
                            st.error("❌ 작업 생성 실패")
                
                with col4:
                    if st.button("🗄️ DB 초기화", key=f"db_init_{agent_id}", help="데이터베이스를 초기화하고 스키마를 재생성합니다"):
                        task_id = create_task(agent_id, "DB_INIT")
                        if task_id:
                            st.success(f"✅ 작업 생성 완료: {task_id}")
                            st.warning("⚠️ 주의: DB 초기화는 모든 데이터를 삭제합니다!")
                        else:
                            st.error("❌ 작업 생성 실패")
                
                # 작업 목록 조회
                st.subheader("작업 목록")
                task_status = st.selectbox(
                    "작업 상태 필터",
                    ["all", "pending", "running", "completed", "failed"],
                    key=f"status_{agent_id}"
                )
                
                tasks = get_agent_tasks(agent_id, task_status)
                
                if tasks:
                    task_data = []
                    for task in tasks:
                        task_data.append({
                            "작업 ID": task.get("task_id", "N/A")[:30] + "...",
                            "작업 타입": task.get("task_type", "N/A"),
                            "상태": task.get("status", "N/A"),
                            "생성 시간": task.get("created_at", "N/A")
                        })
                    
                    st.dataframe(pd.DataFrame(task_data), width='stretch')
                    
                    # 작업 상세 정보
                    if st.checkbox("상세 정보 표시", key=f"detail_{agent_id}"):
                        selected_task_id = st.selectbox(
                            "작업 선택",
                            [task.get("task_id") for task in tasks],
                            key=f"select_{agent_id}"
                        )
                        
                        selected_task = next((t for t in tasks if t.get("task_id") == selected_task_id), None)
                        if selected_task:
                            # 작업 기본 정보
                            st.subheader("작업 정보")
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write(f"**작업 ID:** {selected_task.get('task_id', 'N/A')}")
                                st.write(f"**작업 타입:** {selected_task.get('task_type', 'N/A')}")
                            with col2:
                                st.write(f"**상태:** {selected_task.get('status', 'N/A')}")
                                st.write(f"**생성 시간:** {selected_task.get('created_at', 'N/A')}")
                            
                            # 작업 결과 표시 (Agent가 업로드한 result)
                            result = selected_task.get("result")
                            if result:
                                st.subheader("작업 결과")
                                st.json(result)
                                
                                # 결과 요약 표시
                                if isinstance(result, dict):
                                    if result.get("success"):
                                        st.success("✅ 작업 성공")
                                    else:
                                        st.error(f"❌ 작업 실패: {result.get('error', 'Unknown error')}")
                                    
                                    # 스캔 결과 요약
                                    if "results" in result:
                                        st.info(f"스캔 결과: {len(result.get('results', []))}개 항목")
                            else:
                                st.info("작업 결과가 아직 없습니다.")
                            
                            # 전체 작업 정보 (디버깅용)
                            if st.checkbox("전체 작업 정보 표시", key=f"full_{agent_id}"):
                                st.json(selected_task)
                else:
                    st.info("작업이 없습니다.")
        
    except Exception as e:
        st.error(f"Agent 제어 화면 로드 실패: {str(e)}")
        logger.error(f"Agent control error: {str(e)}")


def show_report_generation():
    """리포트 생성 화면"""
    st.header("📄 리포트 생성")

    try:
        db = get_db()
        with db.get_session() as session:
            scan_repo = ScanResultRepository(session)
            poc_repo = POCReproductionRepository(session)

            # 리포트 옵션
            report_type = st.selectbox("리포트 유형", ["전체", "최근 7일", "특정 기간"])

            # 스캔 결과 조회
            if report_type == "전체":
                scan_results = scan_repo.get_recent(days=365, limit=100)
            elif report_type == "최근 7일":
                scan_results = scan_repo.get_recent(days=7, limit=100)
            else:
                date_range = st.date_input("기간 선택", [])
                if len(date_range) == 2:
                    # 날짜 범위 필터링 로직 추가 가능
                    scan_results = scan_repo.get_recent(days=30, limit=100)
                else:
                    scan_results = []

            # PoC 재현 결과 조회
            poc_reproductions = poc_repo.get_successful_reproductions()

            if st.button("리포트 생성"):
                with st.spinner("리포트 생성 중..."):
                    try:
                        # 리포트 생성기 초기화
                        report_generator = ReportGenerator()
                        
                        # LLM 연결 확인 및 상세 정보 표시
                        llm_gen = report_generator.llm_generator
                        if not llm_gen.client:
                            st.warning("⚠️ LLM이 연결되지 않았습니다.")
                            if not llm_gen.api_key:
                                st.error("❌ OPENAI_API_KEY가 설정되지 않았습니다.")
                                st.info("💡 .env 파일에 OPENAI_API_KEY를 추가하거나 환경 변수로 설정하세요.")
                            else:
                                st.error(f"❌ LLM 초기화 실패 (API Key 길이: {len(llm_gen.api_key)})")
                                st.info("💡 OpenAI API 키가 유효한지 확인하세요.")
                            st.info("LLM 없이 리포트를 생성합니다 (Executive Summary는 기본 템플릿 사용).")
                        else:
                            st.success(f"✅ LLM 연결 성공 (모델: {llm_gen.model})")

                        # 리포트 생성
                        report_id = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                        result = report_generator.generate_report(
                            report_id=report_id,
                            scan_results=[s.to_dict() for s in scan_results],
                            poc_reproductions=[p.to_dict() for p in poc_reproductions]
                        )

                        if result.get("success"):
                            st.success(f"리포트 생성 완료: {result.get('file_path')}")
                            st.info(f"파일 크기: {result.get('file_size')} bytes")
                    except Exception as e:
                        st.error(f"리포트 생성 실패: {str(e)}")
                        logger.error(f"리포트 생성 중 오류: {str(e)}", exc_info=True)

                        # 다운로드 버튼
                        report_path = Path(result.get("file_path"))
                        if report_path.exists():
                            with open(report_path, "rb") as f:
                                st.download_button(
                                    label="리포트 다운로드",
                                    data=f.read(),
                                    file_name=report_path.name,
                                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                                )
                    else:
                        st.error(f"리포트 생성 실패: {result.get('error')}")

    except ProgrammingError as e:
        if "does not exist" in str(e) or "relation" in str(e).lower():
            st.warning("⚠️ 데이터베이스 테이블이 존재하지 않습니다. 데이터베이스를 초기화하세요.")
            st.info("대시보드 페이지에서 '데이터베이스 초기화' 버튼을 클릭하거나 다음 명령어를 실행하세요:")
            st.code("docker exec v2r-app python scripts/utils/reset_db.py", language="bash")
        else:
            st.error(f"리포트 생성 실패: {str(e)}")
            logger.error(f"Report generation error: {str(e)}")
    except Exception as e:
        st.error(f"리포트 생성 실패: {str(e)}")
        logger.error(f"Report generation error: {str(e)}")


if __name__ == "__main__":
    main()

