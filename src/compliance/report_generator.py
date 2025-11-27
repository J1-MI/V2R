"""
CCE 점검 결과 리포트 생성 모듈
XML 및 JSON 형식으로 리포트를 생성합니다.
"""

import json
import xml.etree.ElementTree as ET
from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class ComplianceReportGenerator:
    """CCE 점검 결과 리포트 생성 클래스"""

    def __init__(self):
        pass

    def generate_xml(self, check_result: Dict[str, Any], output_path: Optional[str] = None) -> str:
        """
        XML 형식 리포트 생성

        Args:
            check_result: 점검 결과 딕셔너리
            output_path: 출력 파일 경로 (None이면 문자열 반환)

        Returns:
            XML 문자열 또는 파일 경로
        """
        root = ET.Element("compliance_report")
        root.set("standard", check_result.get("standard", ""))
        root.set("host", check_result.get("host", ""))
        root.set("timestamp", check_result.get("timestamp", ""))

        # 통계
        stats = ET.SubElement(root, "statistics")
        statistics = check_result.get("statistics", {})
        for key, value in statistics.items():
            stat_elem = ET.SubElement(stats, key)
            stat_elem.text = str(value)

        # 점검 항목
        checks_elem = ET.SubElement(root, "checks")
        for check in check_result.get("checks", []):
            check_elem = ET.SubElement(checks_elem, "check")
            check_elem.set("id", check.get("id", ""))
            
            title_elem = ET.SubElement(check_elem, "title")
            title_elem.text = check.get("title", "")
            
            status_elem = ET.SubElement(check_elem, "status")
            status_elem.text = check.get("status", "")
            
            detail_elem = ET.SubElement(check_elem, "detail")
            detail_elem.text = check.get("detail", "")
            
            recommendation_elem = ET.SubElement(check_elem, "recommendation")
            recommendation_elem.text = check.get("recommendation", "")

        # XML 문자열 생성
        xml_string = ET.tostring(root, encoding='unicode', method='xml')
        
        # 들여쓰기 포맷팅
        from xml.dom import minidom
        dom = minidom.parseString(xml_string)
        formatted_xml = dom.toprettyxml(indent="  ")

        if output_path:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            output_file.write_text(formatted_xml, encoding='utf-8')
            logger.info(f"XML 리포트 생성: {output_path}")
            return str(output_file)
        
        return formatted_xml

    def generate_json(self, check_result: Dict[str, Any], output_path: Optional[str] = None) -> str:
        """
        JSON 형식 리포트 생성

        Args:
            check_result: 점검 결과 딕셔너리
            output_path: 출력 파일 경로 (None이면 문자열 반환)

        Returns:
            JSON 문자열 또는 파일 경로
        """
        json_string = json.dumps(check_result, ensure_ascii=False, indent=2)

        if output_path:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            output_file.write_text(json_string, encoding='utf-8')
            logger.info(f"JSON 리포트 생성: {output_path}")
            return str(output_file)
        
        return json_string

    def generate_both(self, check_result: Dict[str, Any], base_path: str) -> Dict[str, str]:
        """
        XML과 JSON 모두 생성

        Args:
            check_result: 점검 결과 딕셔너리
            base_path: 기본 파일 경로 (확장자 제외)

        Returns:
            생성된 파일 경로 딕셔너리
        """
        xml_path = self.generate_xml(check_result, f"{base_path}.xml")
        json_path = self.generate_json(check_result, f"{base_path}.json")
        
        return {
            "xml": xml_path,
            "json": json_path
        }

