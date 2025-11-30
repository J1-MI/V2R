#!/usr/bin/env python3
"""Elasticsearch 컨테이너 패턴 테스트"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.cce.checker import find_cve_lab_containers

containers = find_cve_lab_containers()
print(f"발견된 컨테이너: {len(containers)}개")
for c in containers:
    print(f"  {c['name']} -> {c['service_name']} ({c['service']})")

