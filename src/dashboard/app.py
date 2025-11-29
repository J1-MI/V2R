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
from src.database.repository import ScanResultRepository, POCReproductionRepository
from src.database.models import POCReproduction, POCMetadata
from src.report import ReportGenerator
from src.llm import LLMReportGenerator
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
            ["대시보드", "취약점 리스트", "PoC 재현 결과", "리포트 생성"]
        )

    # 페이지 라우팅
    if page == "대시보드":
        show_dashboard()
    elif page == "취약점 리스트":
        show_vulnerability_list()
    elif page == "PoC 재현 결과":
        show_poc_reproductions()
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

            # 최근 스캔 결과 (전체 / 최신 1건 탭 분리)
            st.subheader("최근 스캔 결과")
            recent_scans = repo.get_recent(days=7, limit=50)

            tab_all, tab_latest = st.tabs(["📄 전체 최근 스캔", "🕒 가장 최근 1건"])

            with tab_all:
                if recent_scans:
                    scan_data = []
                    for scan in recent_scans:
                        scan_data.append({
                            "스캔 ID": (scan.scan_id[:20] + "...") if len(scan.scan_id) > 20 else scan.scan_id,
                            "대상": scan.target_host,
                            "스캐너": scan.scanner_name,
                            "심각도": scan.severity,
                            "상태": scan.status,
                            "스캔 시간": scan.scan_timestamp.strftime("%Y-%m-%d %H:%M")
                        })
                    st.dataframe(pd.DataFrame(scan_data), use_container_width=True)
                else:
                    st.info("최근 스캔 결과가 없습니다.")

            with tab_latest:
                if recent_scans:
                    latest = recent_scans[0]  # get_recent가 최신순 정렬
                    latest_data = [{
                        "스캔 ID": latest.scan_id,
                        "대상": latest.target_host,
                        "스캐너": latest.scanner_name,
                        "심각도": latest.severity,
                        "상태": latest.status,
                        "스캔 시간": latest.scan_timestamp.strftime("%Y-%m-%d %H:%M")
                    }]
                    st.write("가장 최근 스캔 1건")
                    st.table(pd.DataFrame(latest_data))
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
                st.dataframe(df, use_container_width=True)

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
                st.dataframe(df, use_container_width=True)

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
                    # 리포트 생성기 초기화
                    report_generator = ReportGenerator()

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

