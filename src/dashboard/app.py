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

from src.database import get_db
from src.database.repository import ScanResultRepository, POCReproductionRepository
from src.report import ReportGenerator
from src.llm import LLMReportGenerator

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
            for scan in scans:
                normalized = scan.normalized_result or {}
                findings = normalized.get("findings", [])

                for finding in findings:
                    vulnerabilities.append({
                        "ID": finding.get("finding_id", ""),
                        "제목": finding.get("title", "Unknown"),
                        "심각도": finding.get("severity", "Info"),
                        "CVE": ", ".join(finding.get("cve_list", [])),
                        "스캐너": scan.scanner_name,
                        "대상": scan.target_host,
                        "발견일": scan.scan_timestamp.strftime("%Y-%m-%d")
                    })

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

            # 재현 결과 조회
            reproductions = repo.get_by_status("success") + repo.get_by_status("partial")

            if reproductions:
                poc_data = []
                for poc in reproductions:
                    poc_data.append({
                        "재현 ID": poc.reproduction_id[:20] + "...",
                        "상태": poc.status,
                        "신뢰도 점수": poc.reliability_score or "N/A",
                        "대상": poc.target_host,
                        "재현 시간": poc.reproduction_timestamp.strftime("%Y-%m-%d %H:%M")
                    })

                df = pd.DataFrame(poc_data)
                st.dataframe(df, use_container_width=True)

                # 상세 정보
                if st.checkbox("상세 정보 표시"):
                    selected_id = st.selectbox("재현 ID 선택", df["재현 ID"].tolist())
                    # 상세 정보 표시 로직 추가 가능
            else:
                st.info("PoC 재현 결과가 없습니다.")

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

    except Exception as e:
        st.error(f"리포트 생성 실패: {str(e)}")
        logger.error(f"Report generation error: {str(e)}")


if __name__ == "__main__":
    main()

