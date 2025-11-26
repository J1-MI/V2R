"""
GitHub PR 템플릿 생성 모듈
취약점 정보를 기반으로 PR 템플릿을 생성합니다.
"""

import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime

from src.config import PROJECT_ROOT

logger = logging.getLogger(__name__)


class PRTemplateGenerator:
    """PR 템플릿 생성 클래스"""

    def __init__(self):
        """PR 템플릿 생성기 초기화"""
        self.templates_dir = PROJECT_ROOT / "templates"
        self.templates_dir.mkdir(parents=True, exist_ok=True)

    def generate_pr_template(
        self,
        vulnerability: Dict[str, Any],
        poc_reproduction: Optional[Dict[str, Any]] = None,
        patch_recommendation: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        PR 템플릿 생성

        Args:
            vulnerability: 취약점 정보
            poc_reproduction: PoC 재현 결과 (선택)
            patch_recommendation: 패치 권고사항 (선택)

        Returns:
            PR 템플릿 생성 결과
        """
        try:
            # 마크다운 템플릿 생성
            template = self._build_pr_template(
                vulnerability, poc_reproduction, patch_recommendation
            )

            # 파일 저장
            template_id = f"pr_{vulnerability.get('finding_id', 'unknown')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            template_path = self.templates_dir / f"{template_id}.md"

            template_path.write_text(template, encoding="utf-8")

            logger.info(f"PR template generated: {template_path}")

            return {
                "success": True,
                "template_id": template_id,
                "file_path": str(template_path),
                "content": template
            }

        except Exception as e:
            logger.error(f"Failed to generate PR template: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def _build_pr_template(
        self,
        vulnerability: Dict[str, Any],
        poc_reproduction: Optional[Dict[str, Any]],
        patch_recommendation: Optional[str]
    ) -> str:
        """PR 템플릿 내용 구성"""
        template = f"""# 보안 취약점 패치: {vulnerability.get('title', 'Unknown')}

## 취약점 정보

- **심각도**: {vulnerability.get('severity', 'Unknown')}
- **CVE**: {', '.join(vulnerability.get('cve_list', []))}
- **발견일**: {datetime.now().strftime('%Y-%m-%d')}

## 설명

{vulnerability.get('description', '상세 정보 없음')}

"""

        # PoC 재현 결과
        if poc_reproduction:
            template += f"""## PoC 재현 결과

- **재현 상태**: {poc_reproduction.get('status', 'Unknown')}
- **신뢰도 점수**: {poc_reproduction.get('reliability_score', 'N/A')}/100

### 재현 방법

```bash
# PoC 재현 ID: {poc_reproduction.get('reproduction_id', 'Unknown')}
# 상세 재현 방법은 증거 파일 참조
```

"""

        # 권고사항
        if patch_recommendation:
            template += f"""## 패치 권고사항

{patch_recommendation}

"""
        else:
            template += f"""## 패치 권고사항

{vulnerability.get('recommendation', '최신 보안 패치 적용 및 보안 설정 점검을 권장합니다.')}

"""

        # 체크리스트
        template += """## 체크리스트

- [ ] 취약점 패치 적용
- [ ] 재현 테스트 완료
- [ ] 보안 검증 완료
- [ ] 문서 업데이트

## 참고 자료

- 증거 파일: `evidence/` 디렉토리 참조
- 상세 리포트: `reports/` 디렉토리 참조
"""

        return template

