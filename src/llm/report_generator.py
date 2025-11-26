"""
LLM 리포트 생성 모듈
OpenAI API를 사용하여 Executive Summary 및 취약점 요약을 생성합니다.
"""

import logging
from typing import Dict, Any, Optional, List
import json

from src.config import OPENAI_API_KEY, LLM_MODEL

logger = logging.getLogger(__name__)


class LLMReportGenerator:
    """LLM 리포트 생성 클래스"""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Args:
            api_key: OpenAI API 키 (None이면 config에서 읽음)
            model: LLM 모델 (None이면 config에서 읽음)
        """
        self.api_key = api_key or OPENAI_API_KEY
        self.model = model or LLM_MODEL
        self.client = None

        if not self.api_key:
            logger.warning("OpenAI API key not provided")
        else:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key)
                logger.info(f"OpenAI client initialized (model: {self.model})")
            except ImportError:
                logger.error("openai package not installed. Install with: pip install openai")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {str(e)}")

    def generate_executive_summary(
        self,
        scan_results: List[Dict[str, Any]],
        poc_reproductions: List[Dict[str, Any]],
        max_vulnerabilities: int = 10
    ) -> Dict[str, Any]:
        """
        Executive Summary 생성

        Args:
            scan_results: 스캔 결과 리스트
            poc_reproductions: PoC 재현 결과 리스트
            max_vulnerabilities: 포함할 최대 취약점 수

        Returns:
            Executive Summary 딕셔너리
        """
        if not self.client:
            return self._generate_fallback_summary(scan_results, poc_reproductions)

        try:
            # 취약점 요약 생성
            vulnerabilities_summary = self._summarize_vulnerabilities(
                scan_results, poc_reproductions, max_vulnerabilities
            )

            # 프롬프트 구성
            prompt = self._build_executive_summary_prompt(
                vulnerabilities_summary, scan_results, poc_reproductions
            )

            # LLM 호출
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a cybersecurity expert writing executive summaries for vulnerability assessment reports. Provide clear, concise, and actionable summaries."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=1000
            )

            executive_summary = response.choices[0].message.content

            return {
                "executive_summary": executive_summary,
                "vulnerabilities_count": len(vulnerabilities_summary),
                "critical_count": sum(1 for v in vulnerabilities_summary if v.get("severity") == "Critical"),
                "high_count": sum(1 for v in vulnerabilities_summary if v.get("severity") == "High"),
                "model": self.model
            }

        except Exception as e:
            logger.error(f"Failed to generate executive summary: {str(e)}")
            return self._generate_fallback_summary(scan_results, poc_reproductions)

    def generate_vulnerability_summary(
        self,
        vulnerability: Dict[str, Any],
        evidence: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        개별 취약점 요약 생성

        Args:
            vulnerability: 취약점 정보
            evidence: 증거 정보 (선택)

        Returns:
            취약점 요약 텍스트
        """
        if not self.client:
            return self._generate_fallback_vulnerability_summary(vulnerability)

        try:
            prompt = self._build_vulnerability_summary_prompt(vulnerability, evidence)

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a cybersecurity expert providing detailed vulnerability analysis."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=500
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Failed to generate vulnerability summary: {str(e)}")
            return self._generate_fallback_vulnerability_summary(vulnerability)

    def _build_executive_summary_prompt(
        self,
        vulnerabilities: List[Dict[str, Any]],
        scan_results: List[Dict[str, Any]],
        poc_reproductions: List[Dict[str, Any]]
    ) -> str:
        """Executive Summary 프롬프트 구성"""
        prompt = f"""다음 취약점 스캔 결과를 바탕으로 임원진을 위한 Executive Summary를 작성해주세요.

## 스캔 결과 요약
- 총 스캔 결과: {len(scan_results)}건
- PoC 재현 성공: {len([p for p in poc_reproductions if p.get('status') == 'success'])}건

## 주요 취약점 ({len(vulnerabilities)}건)
"""
        for i, vuln in enumerate(vulnerabilities[:10], 1):
            prompt += f"""
{i}. {vuln.get('title', 'Unknown')}
   - 심각도: {vuln.get('severity', 'Unknown')}
   - CVE: {', '.join(vuln.get('cve_list', []))}
   - 설명: {vuln.get('description', '')[:200]}
"""

        prompt += """
## 요구사항
1. 한 페이지 분량의 간결한 요약
2. 비즈니스 영향도 강조
3. 우선순위 기반 권고사항
4. 한국어로 작성

Executive Summary를 작성해주세요:
"""

        return prompt

    def _build_vulnerability_summary_prompt(
        self,
        vulnerability: Dict[str, Any],
        evidence: Optional[Dict[str, Any]]
    ) -> str:
        """취약점 요약 프롬프트 구성"""
        prompt = f"""다음 취약점에 대한 상세 분석을 작성해주세요.

## 취약점 정보
- 제목: {vulnerability.get('title', 'Unknown')}
- 심각도: {vulnerability.get('severity', 'Unknown')}
- CVE: {', '.join(vulnerability.get('cve_list', []))}
- 설명: {vulnerability.get('description', '')}
"""

        if evidence:
            prompt += f"""
## 증거 정보
- 시스템콜 로그: {'있음' if evidence.get('syscalls') else '없음'}
- 네트워크 캡처: {'있음' if evidence.get('network') else '없음'}
- 파일 시스템 변화: {'있음' if evidence.get('fs_diff') else '없음'}
"""

        prompt += """
## 요구사항
1. 취약점의 기술적 설명
2. 공격 시나리오
3. 영향도 분석
4. 권고사항
5. 한국어로 작성

상세 분석을 작성해주세요:
"""

        return prompt

    def _summarize_vulnerabilities(
        self,
        scan_results: List[Dict[str, Any]],
        poc_reproductions: List[Dict[str, Any]],
        max_count: int
    ) -> List[Dict[str, Any]]:
        """취약점 요약 생성"""
        vulnerabilities = []

        # 스캔 결과에서 취약점 추출
        for scan_result in scan_results:
            normalized = scan_result.get("normalized_result", {})
            findings = normalized.get("findings", [])

            for finding in findings:
                vulnerabilities.append({
                    "title": finding.get("title", "Unknown"),
                    "severity": finding.get("severity", "Info"),
                    "description": finding.get("description", ""),
                    "cve_list": finding.get("cve_list", []),
                    "source": finding.get("source", "")
                })

        # 심각도 순으로 정렬
        severity_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3, "Info": 4}
        vulnerabilities.sort(
            key=lambda x: severity_order.get(x.get("severity", "Info"), 4)
        )

        return vulnerabilities[:max_count]

    def _generate_fallback_summary(
        self,
        scan_results: List[Dict[str, Any]],
        poc_reproductions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """LLM 없이 기본 요약 생성"""
        total_scans = len(scan_results)
        successful_pocs = len([p for p in poc_reproductions if p.get("status") == "success"])

        summary = f"""
# 취약점 진단 결과 요약

## 개요
- 총 스캔 결과: {total_scans}건
- PoC 재현 성공: {successful_pocs}건

## 주요 발견사항
스캔 결과를 바탕으로 취약점이 발견되었습니다. 상세 내용은 기술본을 참조하세요.

## 권고사항
1. Critical/High 심각도 취약점 우선 패치
2. PoC 재현이 성공한 취약점 즉시 대응
3. 정기적인 보안 점검 실시
"""

        return {
            "executive_summary": summary,
            "vulnerabilities_count": total_scans,
            "critical_count": 0,
            "high_count": 0,
            "model": "fallback"
        }

    def _generate_fallback_vulnerability_summary(self, vulnerability: Dict[str, Any]) -> str:
        """LLM 없이 기본 취약점 요약 생성"""
        return f"""
## {vulnerability.get('title', 'Unknown')}

**심각도**: {vulnerability.get('severity', 'Unknown')}
**CVE**: {', '.join(vulnerability.get('cve_list', []))}

### 설명
{vulnerability.get('description', '상세 정보 없음')}

### 권고사항
- 최신 보안 패치 적용
- 보안 설정 점검
- 모니터링 강화
"""

