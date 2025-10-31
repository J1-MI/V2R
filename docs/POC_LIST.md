# 신뢰 PoC 목록

## 개요
이 문서는 V2R 프로젝트에서 테스트할 신뢰할 수 있는 PoC(Proof of Concept) 목록을 관리합니다.

## PoC 선정 기준
1. **명확한 CVE 식별자**: 알려진 CVE와 연계
2. **재현 가능성**: 격리 환경에서 안전하게 재현 가능
3. **증거 수집 가능**: 행동 기반 증거 수집이 가능한 유형
4. **비파괴적**: 테스트 환경을 완전히 파괴하지 않는 수준

## PoC 목록

### 1. CVE-2021-44228 (Log4Shell)
- **유형**: RCE (Remote Code Execution)
- **위험도**: Critical
- **재현 환경**: Java 애플리케이션 + 취약 Log4j 버전
- **증거 유형**: 
  - 네트워크 트래픽 (LDAP/JNDI 요청)
  - 로그 파일 (의심스러운 요청 패턴)
- **상태**: [ ] 계획, [ ] 구현, [ ] 테스트 완료

### 2. Command Injection (웹 애플리케이션)
- **유형**: OS Command Injection
- **위험도**: High
- **재현 환경**: 취약 PHP/Python 웹 앱
- **증거 유형**:
  - 시스템콜 로그 (strace)
  - 파일 시스템 변화 (inotify)
  - 네트워크 트래픽 (pcap)
- **상태**: [x] 계획, [ ] 구현, [ ] 테스트 완료

### 3. SQL Injection
- **유형**: SQL Injection
- **위험도**: High
- **재현 환경**: 취약 웹 애플리케이션 + MySQL
- **증거 유형**:
  - 데이터베이스 쿼리 로그
  - 웹 응답 패턴
- **상태**: [x] 계획, [ ] 구현, [ ] 테스트 완료

### 4. Exposed MySQL Service
- **유형**: Misconfiguration
- **위험도**: Medium
- **재현 환경**: 공개된 MySQL 포트 (3306)
- **증거 유형**:
  - 포트 스캔 결과
  - 연결 시도 로그
- **상태**: [x] 계획, [ ] 구현, [ ] 테스트 완료

### 5. Exposed SSH Service (Weak Credentials)
- **유형**: Misconfiguration
- **위험도**: High
- **재현 환경**: 공개된 SSH 포트 + 약한 인증
- **증거 유형**:
  - 인증 실패 로그
  - 포트 스캔 결과
- **상태**: [x] 계획, [ ] 구현, [ ] 테스트 완료

## 참고 출처
- CVE Database: https://cve.mitre.org/
- Exploit-DB: https://www.exploit-db.com/
- OWASP Top 10: https://owasp.org/www-project-top-ten/

## 주의사항
- **절대 exploit 코드를 이 문서에 포함하지 마세요**
- CVE 식별자와 설명만 포함
- 실제 공격 방법은 별도 격리 환경에서만 테스트

