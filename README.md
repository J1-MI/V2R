# 클라우드 기반 취약점 진단·리포트 자동화 시스템 개발
**팀명(가제): V2R (Vuln2Report)**  
**기간:** 약 6주 (2025-10-27 ~ 2025-11-28)
**목표:** AWS 기반 테스트베드에서 자동 취약점 탐지 → PoC 격리 재현(증거수집) → PoC 신뢰도 판정 → ML 우선순위 → LLM 기반 Executive Summary 자동생성 → 개발팀용 PR/패치 템플릿 연계까지의 컨설팅형 워크플로우 MVP 구현

**지원자 유의사항:** 프로젝트 자체 난이도가 어느정도 높다고 판단되어, 학업 또는 취업으로 인해 프로젝트에 집중하기 어려운 경우에는 한번 더 고민 해보시길 부탁 드립니다.

---

## 1. 기획 의도 및 목표
- **기획 의도:** 상용 스캐너/오픈소스 툴로는 부족한 ‘PoC의 진위 검증’과 ‘컨설팅 수준의 리포트 품질’을 확보하고자 합니다. 자동화로 반복 업무를 줄이는 동시에, 재현·증거 기반 검증으로 리포트 신뢰도를 보장하는 파이프라인을 만듭니다.
- **주요 목표:**  
  1. 테스트용 격리 인프라(AWS) 구축 및 취약 애플리케이션 배포  
  2. 스캔 → PoC 인게스트 → 격리 재현 → 행동 기반 증거수집 → 자동 신뢰도 판정 파이프라인 구현  
  3. ML로 취약점 우선순위 보조, LLM으로 임원용 요약 자동 생성 (리포트 자동화)  
  4. 취약점 리포트 기반 개발팀 연계(PR 템플릿 자동생성)로 실무 적용성 확보

---

## 2. 기대효과
- **운영 효율성:** 보고서 초안 자동화로 컨설턴트 문서 작성 시간 절감  
- **대응 속도 개선:** 우선순위 자동화로 패치 의사결정 시간 단축  
- **신뢰성 향상:** PoC 재현·행동 증거 기반 검증으로 가짜 PoC·오탐 감소  
- **인재·역량 확보:** 펜테스팅·클라우드·ML/LLM 실무 역량 강화

---

## 3. 아이디어 상세 내용 & 파트별 핵심 포인트

### A. 인프라(테스트베드)
- **내용:** AWS VPC(격리) + EC2(웹·DB) 또는 컨테이너로 취약앱(DVWA, Juice Shop) 배포. Terraform으로 IaC 관리.
- **핵심 포인트:** 완전 격리, 스냅샷/롤백 가능 이미지(AMI), 증거 저장소(S3) 및 접근제어.

### B. 스캐너 통합 및 인게스천
- **내용:** Nmap/Amass 자산탐지 → Nuclei/OpenVAS 취약점 스캔 → 결과 정규화(공통 스키마).
- **핵심 포인트:** 결과 표준화(메타데이터 포함), PoC 자동 인게스트(출처·해시 포함).

### C. PoC 격리 재현 엔진 & 증거수집
- **내용:** PoC 실행은 컨테이너/경량 VM(예: Docker + Firecracker)에서 수행. 실행 전후 스냅샷, 행동 로그(시스템콜, pcap, FS 변화) 수집.
- **핵심 포인트:** 행동 기반 매칭(정적 성공 여부가 아닌 행위로 검증), 재현 실패 시 자동 롤백, 증거(스크린샷/PCAP/로그) 수집.

### D. PoC 진위 검증 & 신뢰도 점수화
- **내용:** 정적분석(가짜 코드 패턴 탐지) + 동적행동 매칭 → 신뢰도(0~100) 산출. 신뢰도 임계값 이하면 큐레이션(사람 검토).
- **핵심 포인트:** 출처 가중치(Exploit-DB 등), 행동 증거 가중치, 자동/수동 워크플로우 연계.

### E. ML / LLM 연동
- **내용:**  
  - ML: 취약점 메타데이터 기반 우선순위 분류(XGBoost 등).  
  - LLM: 취약점 요약/Executive Summary 자동 생성, RAG로 증거 인용 가능.
- **핵심 포인트:** 휴먼-in-the-loop, LLM 결과는 증거와 함께 제공하여 검증 가능하게 함.

### F. 리포트 자동화 & 개발 연계
- **내용:** python-docx/ReportLab로 기술본 자동생성 + LLM으로 임원요약 작성 → GitHub/GitLab API로 PR/Issue 템플릿 자동 생성.
- **핵심 포인트:** 임원용(한 장 요약) + 기술본(증거 포함) 분리 제공, PR 템플릿에 재현 방법·패치 스니펫 포함.

### G. 대시보드 / UI
- **내용:** Streamlit 또는 React 기반 대시보드: 취약점 리스트, 신뢰도, 증거 다운로드, 리포트 생성 버튼, PR 생성 버튼.
- **핵심 포인트:** 사용성(빠른 검토), 큐레이션 인터페이스(사람 검토/승인).

### 에이전트 정책·전송·명령·서버 파이프라인 예시

#### 3.1 클라이언트별 수집 룰 (Agent-Scoped)
에이전트는 서명된 정책(YAML/JSON)을 pull/push로 동기화하며 우선순위는 `global < client < host` 방식을 따릅니다.
룰 항목 예: include/exclude, 필드 마스킹(정규식 redact), 샘플링/레이트 제한, 로컬 보류 조건.
```yaml
client_id: acme-web
version: 3
rules:
  - include_paths: ["/var/log/nginx/access.log"]
    redact:
      - field: "url.query"
        pattern: "(token|session|pwd)=([^&]+)"
        replace: "$1=***"
  - exclude_paths: ["/var/log/app/debug.log"]
  - sampling:
      match: "event.category == 'web'"
      rate_per_sec: 200
```

#### 3.2 에이전트 -> 서버 전송
메시지는 메타·보안·암호화된 페이로드로 구성됩니다. 추천 필드: nonce, timestamp, agent_id, client_id, key_id, payload_hash(SHA-256) 및 선택적 signature
```json
{
  "meta": { "server_id":"srv-collector-01", "client_id":"acme-web", "agent_id":"agent-10",
            "timestamp":"2025-10-01T02:15:30Z", "nonce":"7c1f...a9" },
  "security": { "enc_alg":"AES-256-GCM", "key_id":"k-2025-09",
                "payload_hash":"sha256:3e9f...b7", "signature":"base64-optional" },
  "ciphertext": "base64-blob"
}

```

#### 3.3 원격 명령 채널
권장 통신 모델은 Pull(heartbeat)이며, 명령의 서명·mTLS·감사 로그를 반드시 적용합니다. 허용 명령 예: RULES_RELOAD, PING, CERT_ROTATE, UPGRADE
```json
{ "job_id":"uuid","type":"RULES_RELOAD","args":{"policy_version":"5"},
  "issued_at":"2025-10-01T02:20:00Z","signature":"base64" }
```

#### 3.4 서버 파이프라인/탐지/조언
수신 로그는 ECS-lite 형태로 정규화·인리치(GeoIP/UA) 되고, 룰 기반 탐지와 ML(rolling metrics/IForest/EWMA)이 결합된 하이브리드 이벤트를 생성합니다. 
LLM Advisor는 RAG(근거 Top-K)로 증거를 인용한 권고(제안)만 제공하며 JSON 스키마로 출력합니다

#### 3.5 핵심 DB 스키마
- 'raw_logs', 'events', 'incidents', 'rules', 'agents' 등
- 운영권고: 파티셔닝, 민감 필드 암호화, RBAC/감사 로깅

---

## 4. 파트별 책임자 (분배에 따라 일부 수정 예정)
- **인프라/아키텍트:** 테스트 VPC, Terraform, 이미지 관리  
- **보안/PoC 담당:** 스캐너 운영, PoC 작성/재현/검증 룰  
- **ML/LLM 엔지니어:** 우선순위 모델, LLM 프롬프트, 임베딩(옵션)  
- **풀스택 개발자:** 파이프라인 API, 리포트 모듈, 대시보드, PR 연동  
- **PM:** 일정·승인·발표·문서관리

---

## 5. 최종 산출물
1. **Terraform 템플릿** — 격리 테스트 VPC 및 인프라 코드  
2. **PoC 재현 엔진 코드** — 컨테이너/VM 오케스트레이션 스크립트(스냅샷·롤백 포함)  
3. **증거 수집 아티팩트** — pcap, syscall logs, FS diff, 스크린샷 (샘플)  
4. **PoC 신뢰도 DB** — PoC 메타데이터(출처·해시·버전·신뢰도)  
5. **스캐너 통합 파이프라인 코드** — 결과 정규화 스크립트  
6. **우선순위 ML 모델** — 학습 코드, 모델 파일, 평가 리포트  
7. **LLM 프롬프트 템플릿 & 리포트 자동화 모듈** — Executive Summary 생성 샘플  
8. **대시보드(웹)** — 취약점 리스트·신뢰도·증거·리포트 다운로드·PR 버튼  
9. **최종 보고서(PDF) & 데모 영상** — 프로젝트 요약·결과·KPI  
10. **README, 운영 절차 문서** — 사용법, 승인/증거보관/파기 정책

---

## 6. 6주 간 일정
> **운영원칙:** 주간 경과보고 1회(각 주 금요일), 매 주 월요일 주간 계획 브리핑 / 수요일 중간 브리핑 || 총 주 3회 

- **Week 0 (사전, 2–3일)**  
  - 레포·Notion 초기화, 역할 확정

- **Week 1 — 인프라 준비 & 테스트앱 배포**  
  - Terraform 기본, VPC/서브넷/보안그룹, DVWA/ Juice Shop 배포, 신뢰 PoC 목록 수집

- **Week 2 — PoC 재현 엔진 & 증거수집 기본 구현**  
  - 컨테이너 재현 스크립트(스냅샷/롤백), strace/tcpdump 자동수집, FS diff

- **Week 3 — 스캐너 통합 및 파이프라인 연결**  
  - Nmap/Nuclei/OpenVAS 연동, 결과 정규화, 인게스천→재현 연계 테스트

- **Week 4 — 리포트 자동화(LLM PoC) 및 대시보드 MVP**  
  - LLM 연동(요약 샘플), python-docx 리포트 템플릿, Streamlit 대시보드 기본

- **Week 5 — ML 우선순위(초안) & PR 연동**  
  - 간단한 우선순위 모델 학습(샘플), GitHub PR 자동화 스크립트

- **Week 6 — 통합테스트, KPI 측정, 문서화, 발표**  
  - 전체 플로우 검증, PoC 재현 성공률·신뢰도 측정, 최종보고서·데모·PPT 준비

---

## 7. 지원 방법
- **지원서식(예시)** 김지민 / kingone750@gmail.com, Discord ID: j1_mi, GitHub 사용자명: J1-MI / 희망 역할(우선순위 1~2) / 관련 경험 및 간단한 기술 스택
- **지원 및 문의:** Discord DM

---
