"""
스캐너 모듈 테스트 스크립트
로컬 환경에서 스캐너 동작을 테스트합니다.
"""

import sys
import json
from pathlib import Path

# 프로젝트 루트 경로 추가
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.scanner.nmap_scanner import NmapScanner
from src.scanner.nuclei_scanner import NucleiScanner
from src.scanner.normalizer import ScanResultNormalizer
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def test_nmap_scanner():
    """Nmap 스캐너 테스트"""
    print("\n=== Nmap Scanner Test ===")
    
    scanner = NmapScanner(scan_timeout=60)
    
    # 로컬 호스트 스캔 (빠른 테스트)
    print("Scanning localhost (ports 22, 80, 443)...")
    result = scanner.quick_scan("127.0.0.1")
    
    print(f"\nScan ID: {result['scan_id']}")
    print(f"Status: {result['status']}")
    print(f"Open Ports: {result['summary']['total_open_ports']}")
    
    if result['summary']['open_ports']:
        print("\nOpen Ports:")
        for port in result['summary']['open_ports']:
            print(f"  - {port['port']}/{port['protocol']}: {port['service']}")
    
    # 결과 저장
    output_file = "test_nmap_result.json"
    scanner.save_results(result, output_file)
    print(f"\nResults saved to: {output_file}")
    
    return result


def test_nuclei_scanner():
    """Nuclei 스캐너 테스트"""
    print("\n=== Nuclei Scanner Test ===")
    
    scanner = NucleiScanner()
    
    # 간단한 웹사이트 스캔
    print("Scanning httpbin.org...")
    result = scanner.scan("https://httpbin.org", severity=["critical", "high"])
    
    print(f"\nScan ID: {result['scan_id']}")
    print(f"Status: {result['status']}")
    print(f"Total Findings: {result['summary']['total_findings']}")
    
    if result['findings']:
        print("\nFindings by Severity:")
        for severity, count in result['summary']['by_severity'].items():
            print(f"  - {severity}: {count}")
    
    # 결과 저장
    output_file = "test_nuclei_result.json"
    scanner.save_results(result, output_file)
    print(f"\nResults saved to: {output_file}")
    
    return result


def test_normalizer():
    """정규화 모듈 테스트"""
    print("\n=== Normalizer Test ===")
    
    normalizer = ScanResultNormalizer()
    
    # 샘플 Nmap 결과
    sample_nmap = {
        "scan_id": "test_nmap_001",
        "scanner_name": "nmap",
        "scan_timestamp": "2025-01-01T00:00:00",
        "target_host": "192.168.1.100",
        "scan_type": "-sV",
        "status": "completed",
        "summary": {
            "open_ports": [
                {
                    "host": "192.168.1.100",
                    "port": 22,
                    "protocol": "tcp",
                    "service": "ssh",
                    "version": "OpenSSH 8.2"
                },
                {
                    "host": "192.168.1.100",
                    "port": 80,
                    "protocol": "tcp",
                    "service": "http",
                    "version": "Apache 2.4.41"
                }
            ]
        }
    }
    
    normalized = normalizer.normalize(sample_nmap, "nmap")
    
    print(f"Normalized Scan ID: {normalized['scan_id']}")
    print(f"Findings Count: {len(normalized['findings'])}")
    print(f"\nFindings:")
    for finding in normalized['findings']:
        print(f"  - [{finding['severity']}] {finding['title']}")
    
    # CVE 추출 테스트
    cves = normalizer.extract_cves(normalized)
    print(f"\nExtracted CVEs: {cves if cves else 'None'}")


def main():
    """메인 테스트 함수"""
    print("=" * 50)
    print("V2R Scanner Module Test")
    print("=" * 50)
    
    # Nmap 테스트 (로컬에서 가능)
    try:
        test_nmap_scanner()
    except Exception as e:
        print(f"\nNmap test failed: {str(e)}")
        print("Note: python-nmap 및 nmap이 설치되어 있어야 합니다.")
    
    # Nuclei 테스트 (Nuclei가 설치되어 있어야 함)
    try:
        test_nuclei_scanner()
    except Exception as e:
        print(f"\nNuclei test failed: {str(e)}")
        print("Note: Nuclei가 설치되어 있어야 합니다.")
    
    # 정규화 테스트 (항상 실행)
    try:
        test_normalizer()
    except Exception as e:
        print(f"\nNormalizer test failed: {str(e)}")
    
    print("\n" + "=" * 50)
    print("Test completed!")
    print("=" * 50)


if __name__ == "__main__":
    main()

