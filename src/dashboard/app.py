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
            ["대시보드", "취약점 리스트", "PoC 재현 결과", "CCE 점검 결과", "리포트 생성"]
        )

    # 페이지 라우팅
    if page == "대시보드":
        show_dashboard()
    elif page == "취약점 리스트":
        show_vulnerability_list()
    elif page == "PoC 재현 결과":
        show_poc_reproductions()
    elif page == "CCE 점검 결과":
        show_cce_compliance()
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

            # 최근 스캔 결과
            st.subheader("최근 스캔 결과")
            recent_scans = repo.get_recent(days=7, limit=10)
            if recent_scans:
                scan_data = []
                for scan in recent_scans:
                    scan_data.append({
                        "스캔 ID": scan.scan_id[:20] + "...",
                        "대상": scan.target_host,
                        "스캐너": scan.scanner_name,
                        "심각도": scan.severity,
                        "상태": scan.status,
                        "스캔 시간": scan.scan_timestamp.strftime("%Y-%m-%d %H:%M")
                    })
                st.dataframe(pd.DataFrame(scan_data), use_container_width=True)
            else:
                st.info("최근 스캔 결과가 없습니다.")

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
            col1, col2, col3 = st.columns(3)
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
            with col3:
                priority_filter = st.selectbox(
                    "우선순위 필터",
                    ["전체", "1 (최우선)", "2", "3", "4", "5 (낮음)"]
                )

            # 스캔 결과 조회
            if severity_filter == "전체":
                scans = repo.get_recent(days=30, limit=100)
            else:
                scans = repo.get_by_severity(severity_filter, limit=100)

            if scanner_filter != "전체":
                scans = [s for s in scans if s.scanner_name == scanner_filter]
            
            # 우선순위 필터 적용
            if priority_filter != "전체":
                target_priority = int(priority_filter.split()[0])
                filtered_scans = []
                for scan in scans:
                    normalized = scan.normalized_result or {}
                    metadata = normalized.get("metadata", {})
                    priority = metadata.get("priority")
                    if priority == target_priority:
                        filtered_scans.append(scan)
                scans = filtered_scans

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


def show_cce_compliance():
    """CCE 점검 결과 화면"""
    st.header("🛡️ CCE 서버 점검 결과")
    
    st.info("전자금융기반시설 2025년도 서버 Linux 항목 점검")
    
    # 점검 실행 섹션
    with st.expander("CCE 점검 실행", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            cce_host = st.text_input("대상 서버 호스트", value="127.0.0.1")
            cce_username = st.text_input("SSH 사용자명", value="root")
            cce_port = st.number_input("SSH 포트", value=22, min_value=1, max_value=65535)
        
        with col2:
            auth_method = st.radio("인증 방법", ["비밀번호", "SSH 키"])
            if auth_method == "비밀번호":
                cce_password = st.text_input("SSH 비밀번호", type="password")
                cce_key_file = None
            else:
                cce_key_file = st.text_input("SSH 키 파일 경로", value="")
                cce_password = None
        
        if st.button("CCE 점검 실행", type="primary"):
            with st.spinner("CCE 점검 실행 중..."):
                try:
                    checker = CCEChecker()
                    result = checker.check_server(
                        host=cce_host,
                        username=cce_username,
                        password=cce_password,
                        key_file=cce_key_file if cce_key_file else None,
                        port=cce_port
                    )
                    
                    if result.get("success"):
                        st.session_state['cce_result'] = result
                        st.success("CCE 점검 완료!")
                        st.rerun()
                    else:
                        st.error(f"CCE 점검 실패: {result.get('error')}")
                except Exception as e:
                    st.error(f"오류 발생: {str(e)}")
    
    # 점검 결과 표시
    if 'cce_result' in st.session_state:
        result = st.session_state['cce_result']
        
        # 통계 표시
        st.subheader("점검 통계")
        stats = result.get("statistics", {})
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("전체 항목", stats.get("total", 0))
        with col2:
            st.metric("양호", stats.get("양호", 0), delta=None, delta_color="normal")
        with col3:
            st.metric("취약", stats.get("취약", 0), delta=None, delta_color="inverse")
        with col4:
            st.metric("주의", stats.get("주의", 0), delta=None, delta_color="off")
        
        # 점검 항목 상세
        st.subheader("점검 항목 상세")
        checks = result.get("checks", [])
        
        if checks:
            check_data = []
            for check in checks:
                status = check.get("status", "")
                status_color = {
                    "양호": "✅",
                    "취약": "❌",
                    "주의": "⚠️"
                }.get(status, "❓")
                
                check_data.append({
                    "ID": check.get("id", ""),
                    "항목": check.get("title", ""),
                    "상태": f"{status_color} {status}",
                    "상세": check.get("detail", ""),
                    "권고사항": check.get("recommendation", "")
                })
            
            df = pd.DataFrame(check_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # 필터링
            st.subheader("필터링")
            filter_status = st.selectbox("상태 필터", ["전체", "양호", "취약", "주의"])
            
            if filter_status != "전체":
                filtered_df = df[df["상태"].str.contains(filter_status)]
                st.dataframe(filtered_df, use_container_width=True, hide_index=True)
            
            # 리포트 다운로드
            st.subheader("리포트 다운로드")
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("XML 리포트 생성"):
                    try:
                        generator = ComplianceReportGenerator()
                        report_id = f"cce_report_{result.get('host', 'unknown').replace('.', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                        xml_path = generator.generate_xml(result, f"reports/{report_id}.xml")
                        st.success(f"XML 리포트 생성 완료: {xml_path}")
                        
                        # 다운로드 버튼
                        with open(xml_path, "rb") as f:
                            st.download_button(
                                label="XML 다운로드",
                                data=f.read(),
                                file_name=f"{report_id}.xml",
                                mime="application/xml"
                            )
                    except Exception as e:
                        st.error(f"리포트 생성 실패: {str(e)}")
            
            with col2:
                if st.button("JSON 리포트 생성"):
                    try:
                        generator = ComplianceReportGenerator()
                        report_id = f"cce_report_{result.get('host', 'unknown').replace('.', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                        json_path = generator.generate_json(result, f"reports/{report_id}.json")
                        st.success(f"JSON 리포트 생성 완료: {json_path}")
                        
                        # 다운로드 버튼
                        with open(json_path, "rb") as f:
                            st.download_button(
                                label="JSON 다운로드",
                                data=f.read(),
                                file_name=f"{report_id}.json",
                                mime="application/json"
                            )
                    except Exception as e:
                        st.error(f"리포트 생성 실패: {str(e)}")
        else:
            st.info("점검 항목이 없습니다.")
    else:
        st.info("CCE 점검을 실행하거나 결과를 불러오세요.")


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

