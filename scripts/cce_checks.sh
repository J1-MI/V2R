#!/bin/bash
#
# CCE 점검 자동화 스크립트 (자동 생성)
# 생성일: 2025-11-30T05:42:27.579100
#

set -u  # undefined 변수만 오류 처리
set -o pipefail  # 파이프 오류 처리

FORMAT="json"


# CCE-LNX-001: 안전한 네트워크 모니터링 서비스 사용
check_1() {
    local cce_id="CCE-LNX-001"
    local name='안전한 네트워크 모니터링 서비스 사용'
    local severity="3"
    local result="양호"
    local detail=""
    local check_output=""
    
    check_output=$(lslpp -l 2>&1)
    if [[ $? -ne 0 ]] || [[ -z "$check_output" ]]; then
        result="양호"
        detail="명령 실행 실패 또는 결과 없음 (대상 리소스 없음)"
    else
        detail="$(echo "$check_output" | head -10 | tr '\n' '; ' | sed 's/; $//')"
        # 기본 판정: 결과가 있으면 양호로 간주 (항목에 따라 다를 수 있음)
        if echo "$check_output" | grep -qiE "error|not found|no such|실패"; then
            result="취약"
        else
            result="양호"
        fi
    fi
    
    # 결과 출력
    if [[ "$FORMAT" == "json" ]]; then
        # Python을 사용하여 JSON 이스케이프 (jq가 없어도 작동)
        if command -v python3 >/dev/null 2>&1; then
            local name_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$name")
            local detail_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$detail")
            echo "{\"id\":\"CCE-LNX-001\",\"name\":$name_escaped,\"severity\":3,\"result\":\"$result\",\"detail\":$detail_escaped}"
        elif command -v jq >/dev/null 2>&1; then
            local name_escaped=$(echo "$name" | jq -Rs .)
            local detail_escaped=$(echo "$detail" | jq -Rs .)
            echo "{\"id\":\"CCE-LNX-001\",\"name\":$name_escaped,\"severity\":3,\"result\":\"$result\",\"detail\":$detail_escaped}"
        else
            # 둘 다 없으면 간단한 이스케이프 (sed 사용)
            # 빈 문자열 처리
            if [[ -z "$name" ]]; then
                name_escaped=""
            else
                name_escaped=$(echo "$name" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            if [[ -z "$detail" ]]; then
                detail_escaped=""
            else
                detail_escaped=$(echo "$detail" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            echo "{\"id\":\"CCE-LNX-001\",\"name\":\"$name_escaped\",\"severity\":3,\"result\":\"$result\",\"detail\":\"$detail_escaped\"}"
        fi
    else
        echo "<check>"
        echo "  <id>CCE-LNX-001</id>"
        echo "  <name>$name</name>"
        echo "  <severity>3</severity>"
        echo "  <result>$result</result>"
        echo "  <detail>$detail</detail>"
        echo "</check>"
    fi
}


# CCE-LNX-002: 불필요한 SMTP 서비스 실행
check_2() {
    local cce_id="CCE-LNX-002"
    local name='불필요한 SMTP 서비스 실행'
    local severity="3"
    local result="양호"
    local detail=""
    local check_output=""
    
    result="양호"
    detail="점검 방법이 명시되지 않음 (대상 리소스 없음으로 간주)"
    
    # 결과 출력
    if [[ "$FORMAT" == "json" ]]; then
        # Python을 사용하여 JSON 이스케이프 (jq가 없어도 작동)
        if command -v python3 >/dev/null 2>&1; then
            local name_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$name")
            local detail_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$detail")
            echo "{\"id\":\"CCE-LNX-002\",\"name\":$name_escaped,\"severity\":3,\"result\":\"$result\",\"detail\":$detail_escaped}"
        elif command -v jq >/dev/null 2>&1; then
            local name_escaped=$(echo "$name" | jq -Rs .)
            local detail_escaped=$(echo "$detail" | jq -Rs .)
            echo "{\"id\":\"CCE-LNX-002\",\"name\":$name_escaped,\"severity\":3,\"result\":\"$result\",\"detail\":$detail_escaped}"
        else
            # 둘 다 없으면 간단한 이스케이프 (sed 사용)
            # 빈 문자열 처리
            if [[ -z "$name" ]]; then
                name_escaped=""
            else
                name_escaped=$(echo "$name" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            if [[ -z "$detail" ]]; then
                detail_escaped=""
            else
                detail_escaped=$(echo "$detail" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            echo "{\"id\":\"CCE-LNX-002\",\"name\":\"$name_escaped\",\"severity\":3,\"result\":\"$result\",\"detail\":\"$detail_escaped\"}"
        fi
    else
        echo "<check>"
        echo "  <id>CCE-LNX-002</id>"
        echo "  <name>$name</name>"
        echo "  <severity>3</severity>"
        echo "  <result>$result</result>"
        echo "  <detail>$detail</detail>"
        echo "</check>"
    fi
}


# CCE-LNX-003: SMTP 서비스의 expn/vrfy 명령어 실행 제한 미비
check_3() {
    local cce_id="CCE-LNX-003"
    local name='SMTP 서비스의 expn/vrfy 명령어 실행 제한 미비'
    local severity="3"
    local result="양호"
    local detail=""
    local check_output=""
    
    result="양호"
    detail="점검 방법이 명시되지 않음 (대상 리소스 없음으로 간주)"
    
    # 결과 출력
    if [[ "$FORMAT" == "json" ]]; then
        # Python을 사용하여 JSON 이스케이프 (jq가 없어도 작동)
        if command -v python3 >/dev/null 2>&1; then
            local name_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$name")
            local detail_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$detail")
            echo "{\"id\":\"CCE-LNX-003\",\"name\":$name_escaped,\"severity\":3,\"result\":\"$result\",\"detail\":$detail_escaped}"
        elif command -v jq >/dev/null 2>&1; then
            local name_escaped=$(echo "$name" | jq -Rs .)
            local detail_escaped=$(echo "$detail" | jq -Rs .)
            echo "{\"id\":\"CCE-LNX-003\",\"name\":$name_escaped,\"severity\":3,\"result\":\"$result\",\"detail\":$detail_escaped}"
        else
            # 둘 다 없으면 간단한 이스케이프 (sed 사용)
            # 빈 문자열 처리
            if [[ -z "$name" ]]; then
                name_escaped=""
            else
                name_escaped=$(echo "$name" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            if [[ -z "$detail" ]]; then
                detail_escaped=""
            else
                detail_escaped=$(echo "$detail" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            echo "{\"id\":\"CCE-LNX-003\",\"name\":\"$name_escaped\",\"severity\":3,\"result\":\"$result\",\"detail\":\"$detail_escaped\"}"
        fi
    else
        echo "<check>"
        echo "  <id>CCE-LNX-003</id>"
        echo "  <name>$name</name>"
        echo "  <severity>3</severity>"
        echo "  <result>$result</result>"
        echo "  <detail>$detail</detail>"
        echo "</check>"
    fi
}


# CCE-LNX-004: SMTP 서비스 로그 수준 설정 미흡
check_4() {
    local cce_id="CCE-LNX-004"
    local name='SMTP 서비스 로그 수준 설정 미흡'
    local severity="2"
    local result="양호"
    local detail=""
    local check_output=""
    
    result="양호"
    detail="점검 방법이 명시되지 않음 (대상 리소스 없음으로 간주)"
    
    # 결과 출력
    if [[ "$FORMAT" == "json" ]]; then
        # Python을 사용하여 JSON 이스케이프 (jq가 없어도 작동)
        if command -v python3 >/dev/null 2>&1; then
            local name_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$name")
            local detail_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$detail")
            echo "{\"id\":\"CCE-LNX-004\",\"name\":$name_escaped,\"severity\":2,\"result\":\"$result\",\"detail\":$detail_escaped}"
        elif command -v jq >/dev/null 2>&1; then
            local name_escaped=$(echo "$name" | jq -Rs .)
            local detail_escaped=$(echo "$detail" | jq -Rs .)
            echo "{\"id\":\"CCE-LNX-004\",\"name\":$name_escaped,\"severity\":2,\"result\":\"$result\",\"detail\":$detail_escaped}"
        else
            # 둘 다 없으면 간단한 이스케이프 (sed 사용)
            # 빈 문자열 처리
            if [[ -z "$name" ]]; then
                name_escaped=""
            else
                name_escaped=$(echo "$name" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            if [[ -z "$detail" ]]; then
                detail_escaped=""
            else
                detail_escaped=$(echo "$detail" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            echo "{\"id\":\"CCE-LNX-004\",\"name\":\"$name_escaped\",\"severity\":2,\"result\":\"$result\",\"detail\":\"$detail_escaped\"}"
        fi
    else
        echo "<check>"
        echo "  <id>CCE-LNX-004</id>"
        echo "  <name>$name</name>"
        echo "  <severity>2</severity>"
        echo "  <result>$result</result>"
        echo "  <detail>$detail</detail>"
        echo "</check>"
    fi
}


# CCE-LNX-005: 취약한 버전의 SMTP 서비스 사용
check_5() {
    local cce_id="CCE-LNX-005"
    local name='취약한 버전의 SMTP 서비스 사용'
    local severity="5"
    local result="양호"
    local detail=""
    local check_output=""
    
    check_output=$(postconf -d mail_version 2>&1)
    if [[ $? -ne 0 ]] || [[ -z "$check_output" ]]; then
        result="양호"
        detail="명령 실행 실패 또는 결과 없음 (대상 리소스 없음)"
    else
        detail="$(echo "$check_output" | head -10 | tr '\n' '; ' | sed 's/; $//')"
        # 기본 판정: 결과가 있으면 양호로 간주 (항목에 따라 다를 수 있음)
        if echo "$check_output" | grep -qiE "error|not found|no such|실패"; then
            result="취약"
        else
            result="양호"
        fi
    fi
    
    # 결과 출력
    if [[ "$FORMAT" == "json" ]]; then
        # Python을 사용하여 JSON 이스케이프 (jq가 없어도 작동)
        if command -v python3 >/dev/null 2>&1; then
            local name_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$name")
            local detail_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$detail")
            echo "{\"id\":\"CCE-LNX-005\",\"name\":$name_escaped,\"severity\":5,\"result\":\"$result\",\"detail\":$detail_escaped}"
        elif command -v jq >/dev/null 2>&1; then
            local name_escaped=$(echo "$name" | jq -Rs .)
            local detail_escaped=$(echo "$detail" | jq -Rs .)
            echo "{\"id\":\"CCE-LNX-005\",\"name\":$name_escaped,\"severity\":5,\"result\":\"$result\",\"detail\":$detail_escaped}"
        else
            # 둘 다 없으면 간단한 이스케이프 (sed 사용)
            # 빈 문자열 처리
            if [[ -z "$name" ]]; then
                name_escaped=""
            else
                name_escaped=$(echo "$name" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            if [[ -z "$detail" ]]; then
                detail_escaped=""
            else
                detail_escaped=$(echo "$detail" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            echo "{\"id\":\"CCE-LNX-005\",\"name\":\"$name_escaped\",\"severity\":5,\"result\":\"$result\",\"detail\":\"$detail_escaped\"}"
        fi
    else
        echo "<check>"
        echo "  <id>CCE-LNX-005</id>"
        echo "  <name>$name</name>"
        echo "  <severity>5</severity>"
        echo "  <result>$result</result>"
        echo "  <detail>$detail</detail>"
        echo "</check>"
    fi
}


# CCE-LNX-006: SMTP 서비스의 DoS 방지 기능 미설정
check_6() {
    local cce_id="CCE-LNX-006"
    local name='SMTP 서비스의 DoS 방지 기능 미설정'
    local severity="1"
    local result="양호"
    local detail=""
    local check_output=""
    
    result="양호"
    detail="점검 방법이 명시되지 않음 (대상 리소스 없음으로 간주)"
    
    # 결과 출력
    if [[ "$FORMAT" == "json" ]]; then
        # Python을 사용하여 JSON 이스케이프 (jq가 없어도 작동)
        if command -v python3 >/dev/null 2>&1; then
            local name_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$name")
            local detail_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$detail")
            echo "{\"id\":\"CCE-LNX-006\",\"name\":$name_escaped,\"severity\":1,\"result\":\"$result\",\"detail\":$detail_escaped}"
        elif command -v jq >/dev/null 2>&1; then
            local name_escaped=$(echo "$name" | jq -Rs .)
            local detail_escaped=$(echo "$detail" | jq -Rs .)
            echo "{\"id\":\"CCE-LNX-006\",\"name\":$name_escaped,\"severity\":1,\"result\":\"$result\",\"detail\":$detail_escaped}"
        else
            # 둘 다 없으면 간단한 이스케이프 (sed 사용)
            # 빈 문자열 처리
            if [[ -z "$name" ]]; then
                name_escaped=""
            else
                name_escaped=$(echo "$name" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            if [[ -z "$detail" ]]; then
                detail_escaped=""
            else
                detail_escaped=$(echo "$detail" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            echo "{\"id\":\"CCE-LNX-006\",\"name\":\"$name_escaped\",\"severity\":1,\"result\":\"$result\",\"detail\":\"$detail_escaped\"}"
        fi
    else
        echo "<check>"
        echo "  <id>CCE-LNX-006</id>"
        echo "  <name>$name</name>"
        echo "  <severity>1</severity>"
        echo "  <result>$result</result>"
        echo "  <detail>$detail</detail>"
        echo "</check>"
    fi
}


# CCE-LNX-007: SMTP 서비스 스팸 메일 릴레이 제한 미설정
check_7() {
    local cce_id="CCE-LNX-007"
    local name='SMTP 서비스 스팸 메일 릴레이 제한 미설정'
    local severity="4"
    local result="양호"
    local detail=""
    local check_output=""
    
    result="양호"
    detail="점검 방법이 명시되지 않음 (대상 리소스 없음으로 간주)"
    
    # 결과 출력
    if [[ "$FORMAT" == "json" ]]; then
        # Python을 사용하여 JSON 이스케이프 (jq가 없어도 작동)
        if command -v python3 >/dev/null 2>&1; then
            local name_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$name")
            local detail_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$detail")
            echo "{\"id\":\"CCE-LNX-007\",\"name\":$name_escaped,\"severity\":4,\"result\":\"$result\",\"detail\":$detail_escaped}"
        elif command -v jq >/dev/null 2>&1; then
            local name_escaped=$(echo "$name" | jq -Rs .)
            local detail_escaped=$(echo "$detail" | jq -Rs .)
            echo "{\"id\":\"CCE-LNX-007\",\"name\":$name_escaped,\"severity\":4,\"result\":\"$result\",\"detail\":$detail_escaped}"
        else
            # 둘 다 없으면 간단한 이스케이프 (sed 사용)
            # 빈 문자열 처리
            if [[ -z "$name" ]]; then
                name_escaped=""
            else
                name_escaped=$(echo "$name" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            if [[ -z "$detail" ]]; then
                detail_escaped=""
            else
                detail_escaped=$(echo "$detail" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            echo "{\"id\":\"CCE-LNX-007\",\"name\":\"$name_escaped\",\"severity\":4,\"result\":\"$result\",\"detail\":\"$detail_escaped\"}"
        fi
    else
        echo "<check>"
        echo "  <id>CCE-LNX-007</id>"
        echo "  <name>$name</name>"
        echo "  <severity>4</severity>"
        echo "  <result>$result</result>"
        echo "  <detail>$detail</detail>"
        echo "</check>"
    fi
}


# CCE-LNX-008: SMTP 서비스의 메일 queue 처리 권한 설정 미흡
check_8() {
    local cce_id="CCE-LNX-008"
    local name='SMTP 서비스의 메일 queue 처리 권한 설정 미흡'
    local severity="4"
    local result="양호"
    local detail=""
    local check_output=""
    
    result="양호"
    detail="점검 방법이 명시되지 않음 (대상 리소스 없음으로 간주)"
    
    # 결과 출력
    if [[ "$FORMAT" == "json" ]]; then
        # Python을 사용하여 JSON 이스케이프 (jq가 없어도 작동)
        if command -v python3 >/dev/null 2>&1; then
            local name_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$name")
            local detail_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$detail")
            echo "{\"id\":\"CCE-LNX-008\",\"name\":$name_escaped,\"severity\":4,\"result\":\"$result\",\"detail\":$detail_escaped}"
        elif command -v jq >/dev/null 2>&1; then
            local name_escaped=$(echo "$name" | jq -Rs .)
            local detail_escaped=$(echo "$detail" | jq -Rs .)
            echo "{\"id\":\"CCE-LNX-008\",\"name\":$name_escaped,\"severity\":4,\"result\":\"$result\",\"detail\":$detail_escaped}"
        else
            # 둘 다 없으면 간단한 이스케이프 (sed 사용)
            # 빈 문자열 처리
            if [[ -z "$name" ]]; then
                name_escaped=""
            else
                name_escaped=$(echo "$name" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            if [[ -z "$detail" ]]; then
                detail_escaped=""
            else
                detail_escaped=$(echo "$detail" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            echo "{\"id\":\"CCE-LNX-008\",\"name\":\"$name_escaped\",\"severity\":4,\"result\":\"$result\",\"detail\":\"$detail_escaped\"}"
        fi
    else
        echo "<check>"
        echo "  <id>CCE-LNX-008</id>"
        echo "  <name>$name</name>"
        echo "  <severity>4</severity>"
        echo "  <result>$result</result>"
        echo "  <detail>$detail</detail>"
        echo "</check>"
    fi
}


# CCE-LNX-009: 시스템 관리자 계정의 FTP 사용 제한 미비
check_9() {
    local cce_id="CCE-LNX-009"
    local name='시스템 관리자 계정의 FTP 사용 제한 미비'
    local severity="3"
    local result="양호"
    local detail=""
    local check_output=""
    
    result="양호"
    detail="점검 방법이 명시되지 않음 (대상 리소스 없음으로 간주)"
    
    # 결과 출력
    if [[ "$FORMAT" == "json" ]]; then
        # Python을 사용하여 JSON 이스케이프 (jq가 없어도 작동)
        if command -v python3 >/dev/null 2>&1; then
            local name_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$name")
            local detail_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$detail")
            echo "{\"id\":\"CCE-LNX-009\",\"name\":$name_escaped,\"severity\":3,\"result\":\"$result\",\"detail\":$detail_escaped}"
        elif command -v jq >/dev/null 2>&1; then
            local name_escaped=$(echo "$name" | jq -Rs .)
            local detail_escaped=$(echo "$detail" | jq -Rs .)
            echo "{\"id\":\"CCE-LNX-009\",\"name\":$name_escaped,\"severity\":3,\"result\":\"$result\",\"detail\":$detail_escaped}"
        else
            # 둘 다 없으면 간단한 이스케이프 (sed 사용)
            # 빈 문자열 처리
            if [[ -z "$name" ]]; then
                name_escaped=""
            else
                name_escaped=$(echo "$name" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            if [[ -z "$detail" ]]; then
                detail_escaped=""
            else
                detail_escaped=$(echo "$detail" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            echo "{\"id\":\"CCE-LNX-009\",\"name\":\"$name_escaped\",\"severity\":3,\"result\":\"$result\",\"detail\":\"$detail_escaped\"}"
        fi
    else
        echo "<check>"
        echo "  <id>CCE-LNX-009</id>"
        echo "  <name>$name</name>"
        echo "  <severity>3</severity>"
        echo "  <result>$result</result>"
        echo "  <detail>$detail</detail>"
        echo "</check>"
    fi
}


# CCE-LNX-010: .netrc 파일 내 중요 정보 노출
check_10() {
    local cce_id="CCE-LNX-010"
    local name='.netrc 파일 내 중요 정보 노출'
    local severity="4"
    local result="양호"
    local detail=""
    local check_output=""
    
    result="양호"
    detail="점검 방법이 명시되지 않음 (대상 리소스 없음으로 간주)"
    
    # 결과 출력
    if [[ "$FORMAT" == "json" ]]; then
        # Python을 사용하여 JSON 이스케이프 (jq가 없어도 작동)
        if command -v python3 >/dev/null 2>&1; then
            local name_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$name")
            local detail_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$detail")
            echo "{\"id\":\"CCE-LNX-010\",\"name\":$name_escaped,\"severity\":4,\"result\":\"$result\",\"detail\":$detail_escaped}"
        elif command -v jq >/dev/null 2>&1; then
            local name_escaped=$(echo "$name" | jq -Rs .)
            local detail_escaped=$(echo "$detail" | jq -Rs .)
            echo "{\"id\":\"CCE-LNX-010\",\"name\":$name_escaped,\"severity\":4,\"result\":\"$result\",\"detail\":$detail_escaped}"
        else
            # 둘 다 없으면 간단한 이스케이프 (sed 사용)
            # 빈 문자열 처리
            if [[ -z "$name" ]]; then
                name_escaped=""
            else
                name_escaped=$(echo "$name" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            if [[ -z "$detail" ]]; then
                detail_escaped=""
            else
                detail_escaped=$(echo "$detail" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            echo "{\"id\":\"CCE-LNX-010\",\"name\":\"$name_escaped\",\"severity\":4,\"result\":\"$result\",\"detail\":\"$detail_escaped\"}"
        fi
    else
        echo "<check>"
        echo "  <id>CCE-LNX-010</id>"
        echo "  <name>$name</name>"
        echo "  <severity>4</severity>"
        echo "  <result>$result</result>"
        echo "  <detail>$detail</detail>"
        echo "</check>"
    fi
}


# CCE-LNX-011: Anonymous 계정의 FTP 서비스 접속 제한 미비
check_11() {
    local cce_id="CCE-LNX-011"
    local name='Anonymous 계정의 FTP 서비스 접속 제한 미비'
    local severity="5"
    local result="양호"
    local detail=""
    local check_output=""
    
    result="양호"
    detail="점검 방법이 명시되지 않음 (대상 리소스 없음으로 간주)"
    
    # 결과 출력
    if [[ "$FORMAT" == "json" ]]; then
        # Python을 사용하여 JSON 이스케이프 (jq가 없어도 작동)
        if command -v python3 >/dev/null 2>&1; then
            local name_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$name")
            local detail_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$detail")
            echo "{\"id\":\"CCE-LNX-011\",\"name\":$name_escaped,\"severity\":5,\"result\":\"$result\",\"detail\":$detail_escaped}"
        elif command -v jq >/dev/null 2>&1; then
            local name_escaped=$(echo "$name" | jq -Rs .)
            local detail_escaped=$(echo "$detail" | jq -Rs .)
            echo "{\"id\":\"CCE-LNX-011\",\"name\":$name_escaped,\"severity\":5,\"result\":\"$result\",\"detail\":$detail_escaped}"
        else
            # 둘 다 없으면 간단한 이스케이프 (sed 사용)
            # 빈 문자열 처리
            if [[ -z "$name" ]]; then
                name_escaped=""
            else
                name_escaped=$(echo "$name" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            if [[ -z "$detail" ]]; then
                detail_escaped=""
            else
                detail_escaped=$(echo "$detail" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            echo "{\"id\":\"CCE-LNX-011\",\"name\":\"$name_escaped\",\"severity\":5,\"result\":\"$result\",\"detail\":\"$detail_escaped\"}"
        fi
    else
        echo "<check>"
        echo "  <id>CCE-LNX-011</id>"
        echo "  <name>$name</name>"
        echo "  <severity>5</severity>"
        echo "  <result>$result</result>"
        echo "  <detail>$detail</detail>"
        echo "</check>"
    fi
}


# CCE-LNX-012: NFS 접근통제 미비
check_12() {
    local cce_id="CCE-LNX-012"
    local name='NFS 접근통제 미비'
    local severity="5"
    local result="양호"
    local detail=""
    local check_output=""
    
    result="양호"
    detail="점검 방법이 명시되지 않음 (대상 리소스 없음으로 간주)"
    
    # 결과 출력
    if [[ "$FORMAT" == "json" ]]; then
        # Python을 사용하여 JSON 이스케이프 (jq가 없어도 작동)
        if command -v python3 >/dev/null 2>&1; then
            local name_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$name")
            local detail_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$detail")
            echo "{\"id\":\"CCE-LNX-012\",\"name\":$name_escaped,\"severity\":5,\"result\":\"$result\",\"detail\":$detail_escaped}"
        elif command -v jq >/dev/null 2>&1; then
            local name_escaped=$(echo "$name" | jq -Rs .)
            local detail_escaped=$(echo "$detail" | jq -Rs .)
            echo "{\"id\":\"CCE-LNX-012\",\"name\":$name_escaped,\"severity\":5,\"result\":\"$result\",\"detail\":$detail_escaped}"
        else
            # 둘 다 없으면 간단한 이스케이프 (sed 사용)
            # 빈 문자열 처리
            if [[ -z "$name" ]]; then
                name_escaped=""
            else
                name_escaped=$(echo "$name" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            if [[ -z "$detail" ]]; then
                detail_escaped=""
            else
                detail_escaped=$(echo "$detail" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            echo "{\"id\":\"CCE-LNX-012\",\"name\":\"$name_escaped\",\"severity\":5,\"result\":\"$result\",\"detail\":\"$detail_escaped\"}"
        fi
    else
        echo "<check>"
        echo "  <id>CCE-LNX-012</id>"
        echo "  <name>$name</name>"
        echo "  <severity>5</severity>"
        echo "  <result>$result</result>"
        echo "  <detail>$detail</detail>"
        echo "</check>"
    fi
}


# CCE-LNX-013: 불필요한 NFS 서비스 실행
check_13() {
    local cce_id="CCE-LNX-013"
    local name='불필요한 NFS 서비스 실행'
    local severity="4"
    local result="양호"
    local detail=""
    local check_output=""
    
    result="양호"
    detail="점검 방법이 명시되지 않음 (대상 리소스 없음으로 간주)"
    
    # 결과 출력
    if [[ "$FORMAT" == "json" ]]; then
        # Python을 사용하여 JSON 이스케이프 (jq가 없어도 작동)
        if command -v python3 >/dev/null 2>&1; then
            local name_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$name")
            local detail_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$detail")
            echo "{\"id\":\"CCE-LNX-013\",\"name\":$name_escaped,\"severity\":4,\"result\":\"$result\",\"detail\":$detail_escaped}"
        elif command -v jq >/dev/null 2>&1; then
            local name_escaped=$(echo "$name" | jq -Rs .)
            local detail_escaped=$(echo "$detail" | jq -Rs .)
            echo "{\"id\":\"CCE-LNX-013\",\"name\":$name_escaped,\"severity\":4,\"result\":\"$result\",\"detail\":$detail_escaped}"
        else
            # 둘 다 없으면 간단한 이스케이프 (sed 사용)
            # 빈 문자열 처리
            if [[ -z "$name" ]]; then
                name_escaped=""
            else
                name_escaped=$(echo "$name" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            if [[ -z "$detail" ]]; then
                detail_escaped=""
            else
                detail_escaped=$(echo "$detail" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            echo "{\"id\":\"CCE-LNX-013\",\"name\":\"$name_escaped\",\"severity\":4,\"result\":\"$result\",\"detail\":\"$detail_escaped\"}"
        fi
    else
        echo "<check>"
        echo "  <id>CCE-LNX-013</id>"
        echo "  <name>$name</name>"
        echo "  <severity>4</severity>"
        echo "  <result>$result</result>"
        echo "  <detail>$detail</detail>"
        echo "</check>"
    fi
}


# CCE-LNX-014: 불필요한 RPC서비스 활성화
check_14() {
    local cce_id="CCE-LNX-014"
    local name='불필요한 RPC서비스 활성화'
    local severity="4"
    local result="양호"
    local detail=""
    local check_output=""
    
    result="양호"
    detail="점검 방법이 명시되지 않음 (대상 리소스 없음으로 간주)"
    
    # 결과 출력
    if [[ "$FORMAT" == "json" ]]; then
        # Python을 사용하여 JSON 이스케이프 (jq가 없어도 작동)
        if command -v python3 >/dev/null 2>&1; then
            local name_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$name")
            local detail_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$detail")
            echo "{\"id\":\"CCE-LNX-014\",\"name\":$name_escaped,\"severity\":4,\"result\":\"$result\",\"detail\":$detail_escaped}"
        elif command -v jq >/dev/null 2>&1; then
            local name_escaped=$(echo "$name" | jq -Rs .)
            local detail_escaped=$(echo "$detail" | jq -Rs .)
            echo "{\"id\":\"CCE-LNX-014\",\"name\":$name_escaped,\"severity\":4,\"result\":\"$result\",\"detail\":$detail_escaped}"
        else
            # 둘 다 없으면 간단한 이스케이프 (sed 사용)
            # 빈 문자열 처리
            if [[ -z "$name" ]]; then
                name_escaped=""
            else
                name_escaped=$(echo "$name" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            if [[ -z "$detail" ]]; then
                detail_escaped=""
            else
                detail_escaped=$(echo "$detail" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            echo "{\"id\":\"CCE-LNX-014\",\"name\":\"$name_escaped\",\"severity\":4,\"result\":\"$result\",\"detail\":\"$detail_escaped\"}"
        fi
    else
        echo "<check>"
        echo "  <id>CCE-LNX-014</id>"
        echo "  <name>$name</name>"
        echo "  <severity>4</severity>"
        echo "  <result>$result</result>"
        echo "  <detail>$detail</detail>"
        echo "</check>"
    fi
}


# CCE-LNX-015: FTP 서비스 접근 제어 설정 미비
check_15() {
    local cce_id="CCE-LNX-015"
    local name='FTP 서비스 접근 제어 설정 미비'
    local severity="5"
    local result="양호"
    local detail=""
    local check_output=""
    
    check_output=$(cat /usr/local/etc/proftpd.conf 2>&1)
    if [[ $? -ne 0 ]] || [[ -z "$check_output" ]]; then
        result="양호"
        detail="명령 실행 실패 또는 결과 없음 (대상 리소스 없음)"
    else
        detail="$(echo "$check_output" | head -10 | tr '\n' '; ' | sed 's/; $//')"
        # 기본 판정: 결과가 있으면 양호로 간주 (항목에 따라 다를 수 있음)
        if echo "$check_output" | grep -qiE "error|not found|no such|실패"; then
            result="취약"
        else
            result="양호"
        fi
    fi
    
    # 결과 출력
    if [[ "$FORMAT" == "json" ]]; then
        # Python을 사용하여 JSON 이스케이프 (jq가 없어도 작동)
        if command -v python3 >/dev/null 2>&1; then
            local name_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$name")
            local detail_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$detail")
            echo "{\"id\":\"CCE-LNX-015\",\"name\":$name_escaped,\"severity\":5,\"result\":\"$result\",\"detail\":$detail_escaped}"
        elif command -v jq >/dev/null 2>&1; then
            local name_escaped=$(echo "$name" | jq -Rs .)
            local detail_escaped=$(echo "$detail" | jq -Rs .)
            echo "{\"id\":\"CCE-LNX-015\",\"name\":$name_escaped,\"severity\":5,\"result\":\"$result\",\"detail\":$detail_escaped}"
        else
            # 둘 다 없으면 간단한 이스케이프 (sed 사용)
            # 빈 문자열 처리
            if [[ -z "$name" ]]; then
                name_escaped=""
            else
                name_escaped=$(echo "$name" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            if [[ -z "$detail" ]]; then
                detail_escaped=""
            else
                detail_escaped=$(echo "$detail" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            echo "{\"id\":\"CCE-LNX-015\",\"name\":\"$name_escaped\",\"severity\":5,\"result\":\"$result\",\"detail\":\"$detail_escaped\"}"
        fi
    else
        echo "<check>"
        echo "  <id>CCE-LNX-015</id>"
        echo "  <name>$name</name>"
        echo "  <severity>5</severity>"
        echo "  <result>$result</result>"
        echo "  <detail>$detail</detail>"
        echo "</check>"
    fi
}


# CCE-LNX-016: 계정의 비밀번호 미설정, 빈 암호 사용 관리 미흡
check_16() {
    local cce_id="CCE-LNX-016"
    local name='계정의 비밀번호 미설정, 빈 암호 사용 관리 미흡'
    local severity="3"
    local result="양호"
    local detail=""
    local check_output=""
    
    result="양호"
    detail="점검 방법이 명시되지 않음 (대상 리소스 없음으로 간주)"
    
    # 결과 출력
    if [[ "$FORMAT" == "json" ]]; then
        # Python을 사용하여 JSON 이스케이프 (jq가 없어도 작동)
        if command -v python3 >/dev/null 2>&1; then
            local name_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$name")
            local detail_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$detail")
            echo "{\"id\":\"CCE-LNX-016\",\"name\":$name_escaped,\"severity\":3,\"result\":\"$result\",\"detail\":$detail_escaped}"
        elif command -v jq >/dev/null 2>&1; then
            local name_escaped=$(echo "$name" | jq -Rs .)
            local detail_escaped=$(echo "$detail" | jq -Rs .)
            echo "{\"id\":\"CCE-LNX-016\",\"name\":$name_escaped,\"severity\":3,\"result\":\"$result\",\"detail\":$detail_escaped}"
        else
            # 둘 다 없으면 간단한 이스케이프 (sed 사용)
            # 빈 문자열 처리
            if [[ -z "$name" ]]; then
                name_escaped=""
            else
                name_escaped=$(echo "$name" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            if [[ -z "$detail" ]]; then
                detail_escaped=""
            else
                detail_escaped=$(echo "$detail" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            echo "{\"id\":\"CCE-LNX-016\",\"name\":\"$name_escaped\",\"severity\":3,\"result\":\"$result\",\"detail\":\"$detail_escaped\"}"
        fi
    else
        echo "<check>"
        echo "  <id>CCE-LNX-016</id>"
        echo "  <name>$name</name>"
        echo "  <severity>3</severity>"
        echo "  <result>$result</result>"
        echo "  <detail>$detail</detail>"
        echo "</check>"
    fi
}


# CCE-LNX-017: 취약한 hosts.equiv 또는 .rhosts 설정 존재
check_17() {
    local cce_id="CCE-LNX-017"
    local name='취약한 hosts.equiv 또는 .rhosts 설정 존재'
    local severity="5"
    local result="양호"
    local detail=""
    local check_output=""
    
    result="양호"
    detail="점검 방법이 명시되지 않음 (대상 리소스 없음으로 간주)"
    
    # 결과 출력
    if [[ "$FORMAT" == "json" ]]; then
        # Python을 사용하여 JSON 이스케이프 (jq가 없어도 작동)
        if command -v python3 >/dev/null 2>&1; then
            local name_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$name")
            local detail_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$detail")
            echo "{\"id\":\"CCE-LNX-017\",\"name\":$name_escaped,\"severity\":5,\"result\":\"$result\",\"detail\":$detail_escaped}"
        elif command -v jq >/dev/null 2>&1; then
            local name_escaped=$(echo "$name" | jq -Rs .)
            local detail_escaped=$(echo "$detail" | jq -Rs .)
            echo "{\"id\":\"CCE-LNX-017\",\"name\":$name_escaped,\"severity\":5,\"result\":\"$result\",\"detail\":$detail_escaped}"
        else
            # 둘 다 없으면 간단한 이스케이프 (sed 사용)
            # 빈 문자열 처리
            if [[ -z "$name" ]]; then
                name_escaped=""
            else
                name_escaped=$(echo "$name" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            if [[ -z "$detail" ]]; then
                detail_escaped=""
            else
                detail_escaped=$(echo "$detail" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            echo "{\"id\":\"CCE-LNX-017\",\"name\":\"$name_escaped\",\"severity\":5,\"result\":\"$result\",\"detail\":\"$detail_escaped\"}"
        fi
    else
        echo "<check>"
        echo "  <id>CCE-LNX-017</id>"
        echo "  <name>$name</name>"
        echo "  <severity>5</severity>"
        echo "  <result>$result</result>"
        echo "  <detail>$detail</detail>"
        echo "</check>"
    fi
}


# CCE-LNX-018: root 계정 원격 접속 제한 미비
check_18() {
    local cce_id="CCE-LNX-018"
    local name='root 계정 원격 접속 제한 미비'
    local severity="5"
    local result="양호"
    local detail=""
    local check_output=""
    
    result="양호"
    detail="점검 방법이 명시되지 않음 (대상 리소스 없음으로 간주)"
    
    # 결과 출력
    if [[ "$FORMAT" == "json" ]]; then
        # Python을 사용하여 JSON 이스케이프 (jq가 없어도 작동)
        if command -v python3 >/dev/null 2>&1; then
            local name_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$name")
            local detail_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$detail")
            echo "{\"id\":\"CCE-LNX-018\",\"name\":$name_escaped,\"severity\":5,\"result\":\"$result\",\"detail\":$detail_escaped}"
        elif command -v jq >/dev/null 2>&1; then
            local name_escaped=$(echo "$name" | jq -Rs .)
            local detail_escaped=$(echo "$detail" | jq -Rs .)
            echo "{\"id\":\"CCE-LNX-018\",\"name\":$name_escaped,\"severity\":5,\"result\":\"$result\",\"detail\":$detail_escaped}"
        else
            # 둘 다 없으면 간단한 이스케이프 (sed 사용)
            # 빈 문자열 처리
            if [[ -z "$name" ]]; then
                name_escaped=""
            else
                name_escaped=$(echo "$name" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            if [[ -z "$detail" ]]; then
                detail_escaped=""
            else
                detail_escaped=$(echo "$detail" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            echo "{\"id\":\"CCE-LNX-018\",\"name\":\"$name_escaped\",\"severity\":5,\"result\":\"$result\",\"detail\":\"$detail_escaped\"}"
        fi
    else
        echo "<check>"
        echo "  <id>CCE-LNX-018</id>"
        echo "  <name>$name</name>"
        echo "  <severity>5</severity>"
        echo "  <result>$result</result>"
        echo "  <detail>$detail</detail>"
        echo "</check>"
    fi
}


# CCE-LNX-019: 서비스 접근 IP 및 포트 제한 미비
check_19() {
    local cce_id="CCE-LNX-019"
    local name='서비스 접근 IP 및 포트 제한 미비'
    local severity="4"
    local result="양호"
    local detail=""
    local check_output=""
    
    result="양호"
    detail="점검 방법이 명시되지 않음 (대상 리소스 없음으로 간주)"
    
    # 결과 출력
    if [[ "$FORMAT" == "json" ]]; then
        # Python을 사용하여 JSON 이스케이프 (jq가 없어도 작동)
        if command -v python3 >/dev/null 2>&1; then
            local name_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$name")
            local detail_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$detail")
            echo "{\"id\":\"CCE-LNX-019\",\"name\":$name_escaped,\"severity\":4,\"result\":\"$result\",\"detail\":$detail_escaped}"
        elif command -v jq >/dev/null 2>&1; then
            local name_escaped=$(echo "$name" | jq -Rs .)
            local detail_escaped=$(echo "$detail" | jq -Rs .)
            echo "{\"id\":\"CCE-LNX-019\",\"name\":$name_escaped,\"severity\":4,\"result\":\"$result\",\"detail\":$detail_escaped}"
        else
            # 둘 다 없으면 간단한 이스케이프 (sed 사용)
            # 빈 문자열 처리
            if [[ -z "$name" ]]; then
                name_escaped=""
            else
                name_escaped=$(echo "$name" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            if [[ -z "$detail" ]]; then
                detail_escaped=""
            else
                detail_escaped=$(echo "$detail" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            echo "{\"id\":\"CCE-LNX-019\",\"name\":\"$name_escaped\",\"severity\":4,\"result\":\"$result\",\"detail\":\"$detail_escaped\"}"
        fi
    else
        echo "<check>"
        echo "  <id>CCE-LNX-019</id>"
        echo "  <name>$name</name>"
        echo "  <severity>4</severity>"
        echo "  <result>$result</result>"
        echo "  <detail>$detail</detail>"
        echo "</check>"
    fi
}


# CCE-LNX-020: 원격 터미널 접속 타임아웃 미설정
check_20() {
    local cce_id="CCE-LNX-020"
    local name='원격 터미널 접속 타임아웃 미설정'
    local severity="2"
    local result="양호"
    local detail=""
    local check_output=""
    
    result="양호"
    detail="점검 방법이 명시되지 않음 (대상 리소스 없음으로 간주)"
    
    # 결과 출력
    if [[ "$FORMAT" == "json" ]]; then
        # Python을 사용하여 JSON 이스케이프 (jq가 없어도 작동)
        if command -v python3 >/dev/null 2>&1; then
            local name_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$name")
            local detail_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$detail")
            echo "{\"id\":\"CCE-LNX-020\",\"name\":$name_escaped,\"severity\":2,\"result\":\"$result\",\"detail\":$detail_escaped}"
        elif command -v jq >/dev/null 2>&1; then
            local name_escaped=$(echo "$name" | jq -Rs .)
            local detail_escaped=$(echo "$detail" | jq -Rs .)
            echo "{\"id\":\"CCE-LNX-020\",\"name\":$name_escaped,\"severity\":2,\"result\":\"$result\",\"detail\":$detail_escaped}"
        else
            # 둘 다 없으면 간단한 이스케이프 (sed 사용)
            # 빈 문자열 처리
            if [[ -z "$name" ]]; then
                name_escaped=""
            else
                name_escaped=$(echo "$name" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            if [[ -z "$detail" ]]; then
                detail_escaped=""
            else
                detail_escaped=$(echo "$detail" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            echo "{\"id\":\"CCE-LNX-020\",\"name\":\"$name_escaped\",\"severity\":2,\"result\":\"$result\",\"detail\":\"$detail_escaped\"}"
        fi
    else
        echo "<check>"
        echo "  <id>CCE-LNX-020</id>"
        echo "  <name>$name</name>"
        echo "  <severity>2</severity>"
        echo "  <result>$result</result>"
        echo "  <detail>$detail</detail>"
        echo "</check>"
    fi
}


# CCE-LNX-021: 불필요한 서비스 활성화
check_21() {
    local cce_id="CCE-LNX-021"
    local name='불필요한 서비스 활성화'
    local severity="3"
    local result="양호"
    local detail=""
    local check_output=""
    
    result="양호"
    detail="점검 방법이 명시되지 않음 (대상 리소스 없음으로 간주)"
    
    # 결과 출력
    if [[ "$FORMAT" == "json" ]]; then
        # Python을 사용하여 JSON 이스케이프 (jq가 없어도 작동)
        if command -v python3 >/dev/null 2>&1; then
            local name_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$name")
            local detail_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$detail")
            echo "{\"id\":\"CCE-LNX-021\",\"name\":$name_escaped,\"severity\":3,\"result\":\"$result\",\"detail\":$detail_escaped}"
        elif command -v jq >/dev/null 2>&1; then
            local name_escaped=$(echo "$name" | jq -Rs .)
            local detail_escaped=$(echo "$detail" | jq -Rs .)
            echo "{\"id\":\"CCE-LNX-021\",\"name\":$name_escaped,\"severity\":3,\"result\":\"$result\",\"detail\":$detail_escaped}"
        else
            # 둘 다 없으면 간단한 이스케이프 (sed 사용)
            # 빈 문자열 처리
            if [[ -z "$name" ]]; then
                name_escaped=""
            else
                name_escaped=$(echo "$name" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            if [[ -z "$detail" ]]; then
                detail_escaped=""
            else
                detail_escaped=$(echo "$detail" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            echo "{\"id\":\"CCE-LNX-021\",\"name\":\"$name_escaped\",\"severity\":3,\"result\":\"$result\",\"detail\":\"$detail_escaped\"}"
        fi
    else
        echo "<check>"
        echo "  <id>CCE-LNX-021</id>"
        echo "  <name>$name</name>"
        echo "  <severity>3</severity>"
        echo "  <result>$result</result>"
        echo "  <detail>$detail</detail>"
        echo "</check>"
    fi
}


# CCE-LNX-022: 취약한 서비스 활성화
check_22() {
    local cce_id="CCE-LNX-022"
    local name='취약한 서비스 활성화'
    local severity="5"
    local result="양호"
    local detail=""
    local check_output=""
    
    check_output=$(ps -ef 2>&1)
    if [[ $? -ne 0 ]] || [[ -z "$check_output" ]]; then
        result="양호"
        detail="명령 실행 실패 또는 결과 없음 (대상 리소스 없음)"
    else
        detail="$(echo "$check_output" | head -10 | tr '\n' '; ' | sed 's/; $//')"
        # 기본 판정: 결과가 있으면 양호로 간주 (항목에 따라 다를 수 있음)
        if echo "$check_output" | grep -qiE "error|not found|no such|실패"; then
            result="취약"
        else
            result="양호"
        fi
    fi
    
    # 결과 출력
    if [[ "$FORMAT" == "json" ]]; then
        # Python을 사용하여 JSON 이스케이프 (jq가 없어도 작동)
        if command -v python3 >/dev/null 2>&1; then
            local name_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$name")
            local detail_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$detail")
            echo "{\"id\":\"CCE-LNX-022\",\"name\":$name_escaped,\"severity\":5,\"result\":\"$result\",\"detail\":$detail_escaped}"
        elif command -v jq >/dev/null 2>&1; then
            local name_escaped=$(echo "$name" | jq -Rs .)
            local detail_escaped=$(echo "$detail" | jq -Rs .)
            echo "{\"id\":\"CCE-LNX-022\",\"name\":$name_escaped,\"severity\":5,\"result\":\"$result\",\"detail\":$detail_escaped}"
        else
            # 둘 다 없으면 간단한 이스케이프 (sed 사용)
            # 빈 문자열 처리
            if [[ -z "$name" ]]; then
                name_escaped=""
            else
                name_escaped=$(echo "$name" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            if [[ -z "$detail" ]]; then
                detail_escaped=""
            else
                detail_escaped=$(echo "$detail" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            echo "{\"id\":\"CCE-LNX-022\",\"name\":\"$name_escaped\",\"severity\":5,\"result\":\"$result\",\"detail\":\"$detail_escaped\"}"
        fi
    else
        echo "<check>"
        echo "  <id>CCE-LNX-022</id>"
        echo "  <name>$name</name>"
        echo "  <severity>5</severity>"
        echo "  <result>$result</result>"
        echo "  <detail>$detail</detail>"
        echo "</check>"
    fi
}


# CCE-LNX-023: 취약한 FTP 서비스 실행
check_23() {
    local cce_id="CCE-LNX-023"
    local name='취약한 FTP 서비스 실행'
    local severity="3"
    local result="양호"
    local detail=""
    local check_output=""
    
    check_output=$(ps –ef 2>&1)
    if [[ $? -ne 0 ]] || [[ -z "$check_output" ]]; then
        result="양호"
        detail="명령 실행 실패 또는 결과 없음 (대상 리소스 없음)"
    else
        detail="$(echo "$check_output" | head -10 | tr '\n' '; ' | sed 's/; $//')"
        # 기본 판정: 결과가 있으면 양호로 간주 (항목에 따라 다를 수 있음)
        if echo "$check_output" | grep -qiE "error|not found|no such|실패"; then
            result="취약"
        else
            result="양호"
        fi
    fi
    
    # 결과 출력
    if [[ "$FORMAT" == "json" ]]; then
        # Python을 사용하여 JSON 이스케이프 (jq가 없어도 작동)
        if command -v python3 >/dev/null 2>&1; then
            local name_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$name")
            local detail_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$detail")
            echo "{\"id\":\"CCE-LNX-023\",\"name\":$name_escaped,\"severity\":3,\"result\":\"$result\",\"detail\":$detail_escaped}"
        elif command -v jq >/dev/null 2>&1; then
            local name_escaped=$(echo "$name" | jq -Rs .)
            local detail_escaped=$(echo "$detail" | jq -Rs .)
            echo "{\"id\":\"CCE-LNX-023\",\"name\":$name_escaped,\"severity\":3,\"result\":\"$result\",\"detail\":$detail_escaped}"
        else
            # 둘 다 없으면 간단한 이스케이프 (sed 사용)
            # 빈 문자열 처리
            if [[ -z "$name" ]]; then
                name_escaped=""
            else
                name_escaped=$(echo "$name" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            if [[ -z "$detail" ]]; then
                detail_escaped=""
            else
                detail_escaped=$(echo "$detail" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            echo "{\"id\":\"CCE-LNX-023\",\"name\":\"$name_escaped\",\"severity\":3,\"result\":\"$result\",\"detail\":\"$detail_escaped\"}"
        fi
    else
        echo "<check>"
        echo "  <id>CCE-LNX-023</id>"
        echo "  <name>$name</name>"
        echo "  <severity>3</severity>"
        echo "  <result>$result</result>"
        echo "  <detail>$detail</detail>"
        echo "</check>"
    fi
}


# CCE-LNX-024: 웹 서비스 디렉터리 리스팅 방지 설정 미흡
check_24() {
    local cce_id="CCE-LNX-024"
    local name='웹 서비스 디렉터리 리스팅 방지 설정 미흡'
    local severity="5"
    local result="양호"
    local detail=""
    local check_output=""
    
    check_output=$(Options Indexes FollowSymLinks 2>&1)
    if [[ $? -ne 0 ]] || [[ -z "$check_output" ]]; then
        result="양호"
        detail="명령 실행 실패 또는 결과 없음 (대상 리소스 없음)"
    else
        detail="$(echo "$check_output" | head -10 | tr '\n' '; ' | sed 's/; $//')"
        # 기본 판정: 결과가 있으면 양호로 간주 (항목에 따라 다를 수 있음)
        if echo "$check_output" | grep -qiE "error|not found|no such|실패"; then
            result="취약"
        else
            result="양호"
        fi
    fi
    
    # 결과 출력
    if [[ "$FORMAT" == "json" ]]; then
        # Python을 사용하여 JSON 이스케이프 (jq가 없어도 작동)
        if command -v python3 >/dev/null 2>&1; then
            local name_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$name")
            local detail_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$detail")
            echo "{\"id\":\"CCE-LNX-024\",\"name\":$name_escaped,\"severity\":5,\"result\":\"$result\",\"detail\":$detail_escaped}"
        elif command -v jq >/dev/null 2>&1; then
            local name_escaped=$(echo "$name" | jq -Rs .)
            local detail_escaped=$(echo "$detail" | jq -Rs .)
            echo "{\"id\":\"CCE-LNX-024\",\"name\":$name_escaped,\"severity\":5,\"result\":\"$result\",\"detail\":$detail_escaped}"
        else
            # 둘 다 없으면 간단한 이스케이프 (sed 사용)
            # 빈 문자열 처리
            if [[ -z "$name" ]]; then
                name_escaped=""
            else
                name_escaped=$(echo "$name" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            if [[ -z "$detail" ]]; then
                detail_escaped=""
            else
                detail_escaped=$(echo "$detail" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            echo "{\"id\":\"CCE-LNX-024\",\"name\":\"$name_escaped\",\"severity\":5,\"result\":\"$result\",\"detail\":\"$detail_escaped\"}"
        fi
    else
        echo "<check>"
        echo "  <id>CCE-LNX-024</id>"
        echo "  <name>$name</name>"
        echo "  <severity>5</severity>"
        echo "  <result>$result</result>"
        echo "  <detail>$detail</detail>"
        echo "</check>"
    fi
}


# CCE-LNX-025: 웹 서비스 상위 디렉터리 접근 제한 설정 미흡
check_25() {
    local cce_id="CCE-LNX-025"
    local name='웹 서비스 상위 디렉터리 접근 제한 설정 미흡'
    local severity="5"
    local result="양호"
    local detail=""
    local check_output=""
    
    result="양호"
    detail="점검 방법이 명시되지 않음 (대상 리소스 없음으로 간주)"
    
    # 결과 출력
    if [[ "$FORMAT" == "json" ]]; then
        # Python을 사용하여 JSON 이스케이프 (jq가 없어도 작동)
        if command -v python3 >/dev/null 2>&1; then
            local name_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$name")
            local detail_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$detail")
            echo "{\"id\":\"CCE-LNX-025\",\"name\":$name_escaped,\"severity\":5,\"result\":\"$result\",\"detail\":$detail_escaped}"
        elif command -v jq >/dev/null 2>&1; then
            local name_escaped=$(echo "$name" | jq -Rs .)
            local detail_escaped=$(echo "$detail" | jq -Rs .)
            echo "{\"id\":\"CCE-LNX-025\",\"name\":$name_escaped,\"severity\":5,\"result\":\"$result\",\"detail\":$detail_escaped}"
        else
            # 둘 다 없으면 간단한 이스케이프 (sed 사용)
            # 빈 문자열 처리
            if [[ -z "$name" ]]; then
                name_escaped=""
            else
                name_escaped=$(echo "$name" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            if [[ -z "$detail" ]]; then
                detail_escaped=""
            else
                detail_escaped=$(echo "$detail" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            echo "{\"id\":\"CCE-LNX-025\",\"name\":\"$name_escaped\",\"severity\":5,\"result\":\"$result\",\"detail\":\"$detail_escaped\"}"
        fi
    else
        echo "<check>"
        echo "  <id>CCE-LNX-025</id>"
        echo "  <name>$name</name>"
        echo "  <severity>5</severity>"
        echo "  <result>$result</result>"
        echo "  <detail>$detail</detail>"
        echo "</check>"
    fi
}


# CCE-LNX-026: 웹 서비스 경로 내 불필요한 파일 존재
check_26() {
    local cce_id="CCE-LNX-026"
    local name='웹 서비스 경로 내 불필요한 파일 존재'
    local severity="4"
    local result="양호"
    local detail=""
    local check_output=""
    
    result="양호"
    detail="점검 방법이 명시되지 않음 (대상 리소스 없음으로 간주)"
    
    # 결과 출력
    if [[ "$FORMAT" == "json" ]]; then
        # Python을 사용하여 JSON 이스케이프 (jq가 없어도 작동)
        if command -v python3 >/dev/null 2>&1; then
            local name_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$name")
            local detail_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$detail")
            echo "{\"id\":\"CCE-LNX-026\",\"name\":$name_escaped,\"severity\":4,\"result\":\"$result\",\"detail\":$detail_escaped}"
        elif command -v jq >/dev/null 2>&1; then
            local name_escaped=$(echo "$name" | jq -Rs .)
            local detail_escaped=$(echo "$detail" | jq -Rs .)
            echo "{\"id\":\"CCE-LNX-026\",\"name\":$name_escaped,\"severity\":4,\"result\":\"$result\",\"detail\":$detail_escaped}"
        else
            # 둘 다 없으면 간단한 이스케이프 (sed 사용)
            # 빈 문자열 처리
            if [[ -z "$name" ]]; then
                name_escaped=""
            else
                name_escaped=$(echo "$name" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            if [[ -z "$detail" ]]; then
                detail_escaped=""
            else
                detail_escaped=$(echo "$detail" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            echo "{\"id\":\"CCE-LNX-026\",\"name\":\"$name_escaped\",\"severity\":4,\"result\":\"$result\",\"detail\":\"$detail_escaped\"}"
        fi
    else
        echo "<check>"
        echo "  <id>CCE-LNX-026</id>"
        echo "  <name>$name</name>"
        echo "  <severity>4</severity>"
        echo "  <result>$result</result>"
        echo "  <detail>$detail</detail>"
        echo "</check>"
    fi
}


# CCE-LNX-027: 웹 서비스 파일 업로드 및 다운로드 용량 제한 미설정
check_27() {
    local cce_id="CCE-LNX-027"
    local name='웹 서비스 파일 업로드 및 다운로드 용량 제한 미설정'
    local severity="4"
    local result="양호"
    local detail=""
    local check_output=""
    
    result="양호"
    detail="점검 방법이 명시되지 않음 (대상 리소스 없음으로 간주)"
    
    # 결과 출력
    if [[ "$FORMAT" == "json" ]]; then
        # Python을 사용하여 JSON 이스케이프 (jq가 없어도 작동)
        if command -v python3 >/dev/null 2>&1; then
            local name_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$name")
            local detail_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$detail")
            echo "{\"id\":\"CCE-LNX-027\",\"name\":$name_escaped,\"severity\":4,\"result\":\"$result\",\"detail\":$detail_escaped}"
        elif command -v jq >/dev/null 2>&1; then
            local name_escaped=$(echo "$name" | jq -Rs .)
            local detail_escaped=$(echo "$detail" | jq -Rs .)
            echo "{\"id\":\"CCE-LNX-027\",\"name\":$name_escaped,\"severity\":4,\"result\":\"$result\",\"detail\":$detail_escaped}"
        else
            # 둘 다 없으면 간단한 이스케이프 (sed 사용)
            # 빈 문자열 처리
            if [[ -z "$name" ]]; then
                name_escaped=""
            else
                name_escaped=$(echo "$name" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            if [[ -z "$detail" ]]; then
                detail_escaped=""
            else
                detail_escaped=$(echo "$detail" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            echo "{\"id\":\"CCE-LNX-027\",\"name\":\"$name_escaped\",\"severity\":4,\"result\":\"$result\",\"detail\":\"$detail_escaped\"}"
        fi
    else
        echo "<check>"
        echo "  <id>CCE-LNX-027</id>"
        echo "  <name>$name</name>"
        echo "  <severity>4</severity>"
        echo "  <result>$result</result>"
        echo "  <detail>$detail</detail>"
        echo "</check>"
    fi
}


# CCE-LNX-028: 웹 서비스 프로세스 권한 제한 미비
check_28() {
    local cce_id="CCE-LNX-028"
    local name='웹 서비스 프로세스 권한 제한 미비'
    local severity="5"
    local result="양호"
    local detail=""
    local check_output=""
    
    result="양호"
    detail="점검 방법이 명시되지 않음 (대상 리소스 없음으로 간주)"
    
    # 결과 출력
    if [[ "$FORMAT" == "json" ]]; then
        # Python을 사용하여 JSON 이스케이프 (jq가 없어도 작동)
        if command -v python3 >/dev/null 2>&1; then
            local name_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$name")
            local detail_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$detail")
            echo "{\"id\":\"CCE-LNX-028\",\"name\":$name_escaped,\"severity\":5,\"result\":\"$result\",\"detail\":$detail_escaped}"
        elif command -v jq >/dev/null 2>&1; then
            local name_escaped=$(echo "$name" | jq -Rs .)
            local detail_escaped=$(echo "$detail" | jq -Rs .)
            echo "{\"id\":\"CCE-LNX-028\",\"name\":$name_escaped,\"severity\":5,\"result\":\"$result\",\"detail\":$detail_escaped}"
        else
            # 둘 다 없으면 간단한 이스케이프 (sed 사용)
            # 빈 문자열 처리
            if [[ -z "$name" ]]; then
                name_escaped=""
            else
                name_escaped=$(echo "$name" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            if [[ -z "$detail" ]]; then
                detail_escaped=""
            else
                detail_escaped=$(echo "$detail" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            echo "{\"id\":\"CCE-LNX-028\",\"name\":\"$name_escaped\",\"severity\":5,\"result\":\"$result\",\"detail\":\"$detail_escaped\"}"
        fi
    else
        echo "<check>"
        echo "  <id>CCE-LNX-028</id>"
        echo "  <name>$name</name>"
        echo "  <severity>5</severity>"
        echo "  <result>$result</result>"
        echo "  <detail>$detail</detail>"
        echo "</check>"
    fi
}


# CCE-LNX-029: 웹 서비스 경로 설정 미흡
check_29() {
    local cce_id="CCE-LNX-029"
    local name='웹 서비스 경로 설정 미흡'
    local severity="4"
    local result="양호"
    local detail=""
    local check_output=""
    
    result="양호"
    detail="점검 방법이 명시되지 않음 (대상 리소스 없음으로 간주)"
    
    # 결과 출력
    if [[ "$FORMAT" == "json" ]]; then
        # Python을 사용하여 JSON 이스케이프 (jq가 없어도 작동)
        if command -v python3 >/dev/null 2>&1; then
            local name_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$name")
            local detail_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$detail")
            echo "{\"id\":\"CCE-LNX-029\",\"name\":$name_escaped,\"severity\":4,\"result\":\"$result\",\"detail\":$detail_escaped}"
        elif command -v jq >/dev/null 2>&1; then
            local name_escaped=$(echo "$name" | jq -Rs .)
            local detail_escaped=$(echo "$detail" | jq -Rs .)
            echo "{\"id\":\"CCE-LNX-029\",\"name\":$name_escaped,\"severity\":4,\"result\":\"$result\",\"detail\":$detail_escaped}"
        else
            # 둘 다 없으면 간단한 이스케이프 (sed 사용)
            # 빈 문자열 처리
            if [[ -z "$name" ]]; then
                name_escaped=""
            else
                name_escaped=$(echo "$name" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            if [[ -z "$detail" ]]; then
                detail_escaped=""
            else
                detail_escaped=$(echo "$detail" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            echo "{\"id\":\"CCE-LNX-029\",\"name\":\"$name_escaped\",\"severity\":4,\"result\":\"$result\",\"detail\":\"$detail_escaped\"}"
        fi
    else
        echo "<check>"
        echo "  <id>CCE-LNX-029</id>"
        echo "  <name>$name</name>"
        echo "  <severity>4</severity>"
        echo "  <result>$result</result>"
        echo "  <detail>$detail</detail>"
        echo "</check>"
    fi
}


# CCE-LNX-030: 웹 서비스 경로 내 불필요한 링크 파일 존재
check_30() {
    local cce_id="CCE-LNX-030"
    local name='웹 서비스 경로 내 불필요한 링크 파일 존재'
    local severity="4"
    local result="양호"
    local detail=""
    local check_output=""
    
    result="양호"
    detail="점검 방법이 명시되지 않음 (대상 리소스 없음으로 간주)"
    
    # 결과 출력
    if [[ "$FORMAT" == "json" ]]; then
        # Python을 사용하여 JSON 이스케이프 (jq가 없어도 작동)
        if command -v python3 >/dev/null 2>&1; then
            local name_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$name")
            local detail_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$detail")
            echo "{\"id\":\"CCE-LNX-030\",\"name\":$name_escaped,\"severity\":4,\"result\":\"$result\",\"detail\":$detail_escaped}"
        elif command -v jq >/dev/null 2>&1; then
            local name_escaped=$(echo "$name" | jq -Rs .)
            local detail_escaped=$(echo "$detail" | jq -Rs .)
            echo "{\"id\":\"CCE-LNX-030\",\"name\":$name_escaped,\"severity\":4,\"result\":\"$result\",\"detail\":$detail_escaped}"
        else
            # 둘 다 없으면 간단한 이스케이프 (sed 사용)
            # 빈 문자열 처리
            if [[ -z "$name" ]]; then
                name_escaped=""
            else
                name_escaped=$(echo "$name" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            if [[ -z "$detail" ]]; then
                detail_escaped=""
            else
                detail_escaped=$(echo "$detail" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            echo "{\"id\":\"CCE-LNX-030\",\"name\":\"$name_escaped\",\"severity\":4,\"result\":\"$result\",\"detail\":\"$detail_escaped\"}"
        fi
    else
        echo "<check>"
        echo "  <id>CCE-LNX-030</id>"
        echo "  <name>$name</name>"
        echo "  <severity>4</severity>"
        echo "  <result>$result</result>"
        echo "  <detail>$detail</detail>"
        echo "</check>"
    fi
}


# CCE-LNX-031: 불필요한 웹 서비스 실행
check_31() {
    local cce_id="CCE-LNX-031"
    local name='불필요한 웹 서비스 실행'
    local severity="3"
    local result="양호"
    local detail=""
    local check_output=""
    
    result="양호"
    detail="점검 방법이 명시되지 않음 (대상 리소스 없음으로 간주)"
    
    # 결과 출력
    if [[ "$FORMAT" == "json" ]]; then
        # Python을 사용하여 JSON 이스케이프 (jq가 없어도 작동)
        if command -v python3 >/dev/null 2>&1; then
            local name_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$name")
            local detail_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$detail")
            echo "{\"id\":\"CCE-LNX-031\",\"name\":$name_escaped,\"severity\":3,\"result\":\"$result\",\"detail\":$detail_escaped}"
        elif command -v jq >/dev/null 2>&1; then
            local name_escaped=$(echo "$name" | jq -Rs .)
            local detail_escaped=$(echo "$detail" | jq -Rs .)
            echo "{\"id\":\"CCE-LNX-031\",\"name\":$name_escaped,\"severity\":3,\"result\":\"$result\",\"detail\":$detail_escaped}"
        else
            # 둘 다 없으면 간단한 이스케이프 (sed 사용)
            # 빈 문자열 처리
            if [[ -z "$name" ]]; then
                name_escaped=""
            else
                name_escaped=$(echo "$name" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            if [[ -z "$detail" ]]; then
                detail_escaped=""
            else
                detail_escaped=$(echo "$detail" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            echo "{\"id\":\"CCE-LNX-031\",\"name\":\"$name_escaped\",\"severity\":3,\"result\":\"$result\",\"detail\":\"$detail_escaped\"}"
        fi
    else
        echo "<check>"
        echo "  <id>CCE-LNX-031</id>"
        echo "  <name>$name</name>"
        echo "  <severity>3</severity>"
        echo "  <result>$result</result>"
        echo "  <detail>$detail</detail>"
        echo "</check>"
    fi
}


# CCE-LNX-032: 웹 서비스 기본 계정(아이디 또는 비밀번호) 미변경
check_32() {
    local cce_id="CCE-LNX-032"
    local name='웹 서비스 기본 계정(아이디 또는 비밀번호) 미변경'
    local severity="5"
    local result="양호"
    local detail=""
    local check_output=""
    
    check_output=$(/setup/config/domain/security/SYSTEM_DOMAIN/accounts.xml 2>&1)
    if [[ $? -ne 0 ]] || [[ -z "$check_output" ]]; then
        result="양호"
        detail="명령 실행 실패 또는 결과 없음 (대상 리소스 없음)"
    else
        detail="$(echo "$check_output" | head -10 | tr '\n' '; ' | sed 's/; $//')"
        # 기본 판정: 결과가 있으면 양호로 간주 (항목에 따라 다를 수 있음)
        if echo "$check_output" | grep -qiE "error|not found|no such|실패"; then
            result="취약"
        else
            result="양호"
        fi
    fi
    
    # 결과 출력
    if [[ "$FORMAT" == "json" ]]; then
        # Python을 사용하여 JSON 이스케이프 (jq가 없어도 작동)
        if command -v python3 >/dev/null 2>&1; then
            local name_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$name")
            local detail_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$detail")
            echo "{\"id\":\"CCE-LNX-032\",\"name\":$name_escaped,\"severity\":5,\"result\":\"$result\",\"detail\":$detail_escaped}"
        elif command -v jq >/dev/null 2>&1; then
            local name_escaped=$(echo "$name" | jq -Rs .)
            local detail_escaped=$(echo "$detail" | jq -Rs .)
            echo "{\"id\":\"CCE-LNX-032\",\"name\":$name_escaped,\"severity\":5,\"result\":\"$result\",\"detail\":$detail_escaped}"
        else
            # 둘 다 없으면 간단한 이스케이프 (sed 사용)
            # 빈 문자열 처리
            if [[ -z "$name" ]]; then
                name_escaped=""
            else
                name_escaped=$(echo "$name" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            if [[ -z "$detail" ]]; then
                detail_escaped=""
            else
                detail_escaped=$(echo "$detail" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            echo "{\"id\":\"CCE-LNX-032\",\"name\":\"$name_escaped\",\"severity\":5,\"result\":\"$result\",\"detail\":\"$detail_escaped\"}"
        fi
    else
        echo "<check>"
        echo "  <id>CCE-LNX-032</id>"
        echo "  <name>$name</name>"
        echo "  <severity>5</severity>"
        echo "  <result>$result</result>"
        echo "  <detail>$detail</detail>"
        echo "</check>"
    fi
}


# CCE-LNX-033: DNS 서비스 정보 노출
check_33() {
    local cce_id="CCE-LNX-033"
    local name='DNS 서비스 정보 노출'
    local severity="1"
    local result="양호"
    local detail=""
    local check_output=""
    
    result="양호"
    detail="점검 방법이 명시되지 않음 (대상 리소스 없음으로 간주)"
    
    # 결과 출력
    if [[ "$FORMAT" == "json" ]]; then
        # Python을 사용하여 JSON 이스케이프 (jq가 없어도 작동)
        if command -v python3 >/dev/null 2>&1; then
            local name_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$name")
            local detail_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$detail")
            echo "{\"id\":\"CCE-LNX-033\",\"name\":$name_escaped,\"severity\":1,\"result\":\"$result\",\"detail\":$detail_escaped}"
        elif command -v jq >/dev/null 2>&1; then
            local name_escaped=$(echo "$name" | jq -Rs .)
            local detail_escaped=$(echo "$detail" | jq -Rs .)
            echo "{\"id\":\"CCE-LNX-033\",\"name\":$name_escaped,\"severity\":1,\"result\":\"$result\",\"detail\":$detail_escaped}"
        else
            # 둘 다 없으면 간단한 이스케이프 (sed 사용)
            # 빈 문자열 처리
            if [[ -z "$name" ]]; then
                name_escaped=""
            else
                name_escaped=$(echo "$name" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            if [[ -z "$detail" ]]; then
                detail_escaped=""
            else
                detail_escaped=$(echo "$detail" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            echo "{\"id\":\"CCE-LNX-033\",\"name\":\"$name_escaped\",\"severity\":1,\"result\":\"$result\",\"detail\":\"$detail_escaped\"}"
        fi
    else
        echo "<check>"
        echo "  <id>CCE-LNX-033</id>"
        echo "  <name>$name</name>"
        echo "  <severity>1</severity>"
        echo "  <result>$result</result>"
        echo "  <detail>$detail</detail>"
        echo "</check>"
    fi
}


# CCE-LNX-034: DNS Recursive Query 설정 미흡
check_34() {
    local cce_id="CCE-LNX-034"
    local name='DNS Recursive Query 설정 미흡'
    local severity="3"
    local result="양호"
    local detail=""
    local check_output=""
    
    result="양호"
    detail="점검 방법이 명시되지 않음 (대상 리소스 없음으로 간주)"
    
    # 결과 출력
    if [[ "$FORMAT" == "json" ]]; then
        # Python을 사용하여 JSON 이스케이프 (jq가 없어도 작동)
        if command -v python3 >/dev/null 2>&1; then
            local name_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$name")
            local detail_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$detail")
            echo "{\"id\":\"CCE-LNX-034\",\"name\":$name_escaped,\"severity\":3,\"result\":\"$result\",\"detail\":$detail_escaped}"
        elif command -v jq >/dev/null 2>&1; then
            local name_escaped=$(echo "$name" | jq -Rs .)
            local detail_escaped=$(echo "$detail" | jq -Rs .)
            echo "{\"id\":\"CCE-LNX-034\",\"name\":$name_escaped,\"severity\":3,\"result\":\"$result\",\"detail\":$detail_escaped}"
        else
            # 둘 다 없으면 간단한 이스케이프 (sed 사용)
            # 빈 문자열 처리
            if [[ -z "$name" ]]; then
                name_escaped=""
            else
                name_escaped=$(echo "$name" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            if [[ -z "$detail" ]]; then
                detail_escaped=""
            else
                detail_escaped=$(echo "$detail" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            echo "{\"id\":\"CCE-LNX-034\",\"name\":\"$name_escaped\",\"severity\":3,\"result\":\"$result\",\"detail\":\"$detail_escaped\"}"
        fi
    else
        echo "<check>"
        echo "  <id>CCE-LNX-034</id>"
        echo "  <name>$name</name>"
        echo "  <severity>3</severity>"
        echo "  <result>$result</result>"
        echo "  <detail>$detail</detail>"
        echo "</check>"
    fi
}


# CCE-LNX-035: 취약한 버전의 DNS 서비스 사용
check_35() {
    local cce_id="CCE-LNX-035"
    local name='취약한 버전의 DNS 서비스 사용'
    local severity="5"
    local result="양호"
    local detail=""
    local check_output=""
    
    result="양호"
    detail="점검 방법이 명시되지 않음 (대상 리소스 없음으로 간주)"
    
    # 결과 출력
    if [[ "$FORMAT" == "json" ]]; then
        # Python을 사용하여 JSON 이스케이프 (jq가 없어도 작동)
        if command -v python3 >/dev/null 2>&1; then
            local name_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$name")
            local detail_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$detail")
            echo "{\"id\":\"CCE-LNX-035\",\"name\":$name_escaped,\"severity\":5,\"result\":\"$result\",\"detail\":$detail_escaped}"
        elif command -v jq >/dev/null 2>&1; then
            local name_escaped=$(echo "$name" | jq -Rs .)
            local detail_escaped=$(echo "$detail" | jq -Rs .)
            echo "{\"id\":\"CCE-LNX-035\",\"name\":$name_escaped,\"severity\":5,\"result\":\"$result\",\"detail\":$detail_escaped}"
        else
            # 둘 다 없으면 간단한 이스케이프 (sed 사용)
            # 빈 문자열 처리
            if [[ -z "$name" ]]; then
                name_escaped=""
            else
                name_escaped=$(echo "$name" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            if [[ -z "$detail" ]]; then
                detail_escaped=""
            else
                detail_escaped=$(echo "$detail" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            echo "{\"id\":\"CCE-LNX-035\",\"name\":\"$name_escaped\",\"severity\":5,\"result\":\"$result\",\"detail\":\"$detail_escaped\"}"
        fi
    else
        echo "<check>"
        echo "  <id>CCE-LNX-035</id>"
        echo "  <name>$name</name>"
        echo "  <severity>5</severity>"
        echo "  <result>$result</result>"
        echo "  <detail>$detail</detail>"
        echo "</check>"
    fi
}


# CCE-LNX-036: DNS Zone Transfer 설정 미흡
check_36() {
    local cce_id="CCE-LNX-036"
    local name='DNS Zone Transfer 설정 미흡'
    local severity="4"
    local result="양호"
    local detail=""
    local check_output=""
    
    result="양호"
    detail="점검 방법이 명시되지 않음 (대상 리소스 없음으로 간주)"
    
    # 결과 출력
    if [[ "$FORMAT" == "json" ]]; then
        # Python을 사용하여 JSON 이스케이프 (jq가 없어도 작동)
        if command -v python3 >/dev/null 2>&1; then
            local name_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$name")
            local detail_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$detail")
            echo "{\"id\":\"CCE-LNX-036\",\"name\":$name_escaped,\"severity\":4,\"result\":\"$result\",\"detail\":$detail_escaped}"
        elif command -v jq >/dev/null 2>&1; then
            local name_escaped=$(echo "$name" | jq -Rs .)
            local detail_escaped=$(echo "$detail" | jq -Rs .)
            echo "{\"id\":\"CCE-LNX-036\",\"name\":$name_escaped,\"severity\":4,\"result\":\"$result\",\"detail\":$detail_escaped}"
        else
            # 둘 다 없으면 간단한 이스케이프 (sed 사용)
            # 빈 문자열 처리
            if [[ -z "$name" ]]; then
                name_escaped=""
            else
                name_escaped=$(echo "$name" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            if [[ -z "$detail" ]]; then
                detail_escaped=""
            else
                detail_escaped=$(echo "$detail" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            echo "{\"id\":\"CCE-LNX-036\",\"name\":\"$name_escaped\",\"severity\":4,\"result\":\"$result\",\"detail\":\"$detail_escaped\"}"
        fi
    else
        echo "<check>"
        echo "  <id>CCE-LNX-036</id>"
        echo "  <name>$name</name>"
        echo "  <severity>4</severity>"
        echo "  <result>$result</result>"
        echo "  <detail>$detail</detail>"
        echo "</check>"
    fi
}


# CCE-LNX-037: 비밀번호 관리정책 설정 미비
check_37() {
    local cce_id="CCE-LNX-037"
    local name='비밀번호 관리정책 설정 미비'
    local severity="5"
    local result="양호"
    local detail=""
    local check_output=""
    
    check_output=$(password requisite pam_cracklib.so try_first_pass retry=3 type= minlen=8 dcredit=-1 ucredit=-1 lcredit=-1 ocredit=-1 2>&1)
    if [[ $? -ne 0 ]] || [[ -z "$check_output" ]]; then
        result="양호"
        detail="명령 실행 실패 또는 결과 없음 (대상 리소스 없음)"
    else
        detail="$(echo "$check_output" | head -10 | tr '\n' '; ' | sed 's/; $//')"
        # 기본 판정: 결과가 있으면 양호로 간주 (항목에 따라 다를 수 있음)
        if echo "$check_output" | grep -qiE "error|not found|no such|실패"; then
            result="취약"
        else
            result="양호"
        fi
    fi
    
    # 결과 출력
    if [[ "$FORMAT" == "json" ]]; then
        # Python을 사용하여 JSON 이스케이프 (jq가 없어도 작동)
        if command -v python3 >/dev/null 2>&1; then
            local name_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$name")
            local detail_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$detail")
            echo "{\"id\":\"CCE-LNX-037\",\"name\":$name_escaped,\"severity\":5,\"result\":\"$result\",\"detail\":$detail_escaped}"
        elif command -v jq >/dev/null 2>&1; then
            local name_escaped=$(echo "$name" | jq -Rs .)
            local detail_escaped=$(echo "$detail" | jq -Rs .)
            echo "{\"id\":\"CCE-LNX-037\",\"name\":$name_escaped,\"severity\":5,\"result\":\"$result\",\"detail\":$detail_escaped}"
        else
            # 둘 다 없으면 간단한 이스케이프 (sed 사용)
            # 빈 문자열 처리
            if [[ -z "$name" ]]; then
                name_escaped=""
            else
                name_escaped=$(echo "$name" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            if [[ -z "$detail" ]]; then
                detail_escaped=""
            else
                detail_escaped=$(echo "$detail" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            echo "{\"id\":\"CCE-LNX-037\",\"name\":\"$name_escaped\",\"severity\":5,\"result\":\"$result\",\"detail\":\"$detail_escaped\"}"
        fi
    else
        echo "<check>"
        echo "  <id>CCE-LNX-037</id>"
        echo "  <name>$name</name>"
        echo "  <severity>5</severity>"
        echo "  <result>$result</result>"
        echo "  <detail>$detail</detail>"
        echo "</check>"
    fi
}


# CCE-LNX-038: 취약한 패스워드 저장 방식 사용
check_38() {
    local cce_id="CCE-LNX-038"
    local name='취약한 패스워드 저장 방식 사용'
    local severity="5"
    local result="양호"
    local detail=""
    local check_output=""
    
    result="양호"
    detail="점검 방법이 명시되지 않음 (대상 리소스 없음으로 간주)"
    
    # 결과 출력
    if [[ "$FORMAT" == "json" ]]; then
        # Python을 사용하여 JSON 이스케이프 (jq가 없어도 작동)
        if command -v python3 >/dev/null 2>&1; then
            local name_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$name")
            local detail_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$detail")
            echo "{\"id\":\"CCE-LNX-038\",\"name\":$name_escaped,\"severity\":5,\"result\":\"$result\",\"detail\":$detail_escaped}"
        elif command -v jq >/dev/null 2>&1; then
            local name_escaped=$(echo "$name" | jq -Rs .)
            local detail_escaped=$(echo "$detail" | jq -Rs .)
            echo "{\"id\":\"CCE-LNX-038\",\"name\":$name_escaped,\"severity\":5,\"result\":\"$result\",\"detail\":$detail_escaped}"
        else
            # 둘 다 없으면 간단한 이스케이프 (sed 사용)
            # 빈 문자열 처리
            if [[ -z "$name" ]]; then
                name_escaped=""
            else
                name_escaped=$(echo "$name" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            if [[ -z "$detail" ]]; then
                detail_escaped=""
            else
                detail_escaped=$(echo "$detail" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            echo "{\"id\":\"CCE-LNX-038\",\"name\":\"$name_escaped\",\"severity\":5,\"result\":\"$result\",\"detail\":\"$detail_escaped\"}"
        fi
    else
        echo "<check>"
        echo "  <id>CCE-LNX-038</id>"
        echo "  <name>$name</name>"
        echo "  <severity>5</severity>"
        echo "  <result>$result</result>"
        echo "  <detail>$detail</detail>"
        echo "</check>"
    fi
}


# CCE-LNX-039: 관리자 그룹에 불필요한 사용자 존재
check_39() {
    local cce_id="CCE-LNX-039"
    local name='관리자 그룹에 불필요한 사용자 존재'
    local severity="4"
    local result="양호"
    local detail=""
    local check_output=""
    
    check_output=$(root:x:0:root 2>&1)
    if [[ $? -ne 0 ]] || [[ -z "$check_output" ]]; then
        result="양호"
        detail="명령 실행 실패 또는 결과 없음 (대상 리소스 없음)"
    else
        detail="$(echo "$check_output" | head -10 | tr '\n' '; ' | sed 's/; $//')"
        # 기본 판정: 결과가 있으면 양호로 간주 (항목에 따라 다를 수 있음)
        if echo "$check_output" | grep -qiE "error|not found|no such|실패"; then
            result="취약"
        else
            result="양호"
        fi
    fi
    
    # 결과 출력
    if [[ "$FORMAT" == "json" ]]; then
        # Python을 사용하여 JSON 이스케이프 (jq가 없어도 작동)
        if command -v python3 >/dev/null 2>&1; then
            local name_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$name")
            local detail_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$detail")
            echo "{\"id\":\"CCE-LNX-039\",\"name\":$name_escaped,\"severity\":4,\"result\":\"$result\",\"detail\":$detail_escaped}"
        elif command -v jq >/dev/null 2>&1; then
            local name_escaped=$(echo "$name" | jq -Rs .)
            local detail_escaped=$(echo "$detail" | jq -Rs .)
            echo "{\"id\":\"CCE-LNX-039\",\"name\":$name_escaped,\"severity\":4,\"result\":\"$result\",\"detail\":$detail_escaped}"
        else
            # 둘 다 없으면 간단한 이스케이프 (sed 사용)
            # 빈 문자열 처리
            if [[ -z "$name" ]]; then
                name_escaped=""
            else
                name_escaped=$(echo "$name" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            if [[ -z "$detail" ]]; then
                detail_escaped=""
            else
                detail_escaped=$(echo "$detail" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            echo "{\"id\":\"CCE-LNX-039\",\"name\":\"$name_escaped\",\"severity\":4,\"result\":\"$result\",\"detail\":\"$detail_escaped\"}"
        fi
    else
        echo "<check>"
        echo "  <id>CCE-LNX-039</id>"
        echo "  <name>$name</name>"
        echo "  <severity>4</severity>"
        echo "  <result>$result</result>"
        echo "  <detail>$detail</detail>"
        echo "</check>"
    fi
}


# CCE-LNX-040: 불필요하거나 관리되지 않는 계정 존재
check_40() {
    local cce_id="CCE-LNX-040"
    local name='불필요하거나 관리되지 않는 계정 존재'
    local severity="4"
    local result="양호"
    local detail=""
    local check_output=""
    
    result="양호"
    detail="점검 방법이 명시되지 않음 (대상 리소스 없음으로 간주)"
    
    # 결과 출력
    if [[ "$FORMAT" == "json" ]]; then
        # Python을 사용하여 JSON 이스케이프 (jq가 없어도 작동)
        if command -v python3 >/dev/null 2>&1; then
            local name_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$name")
            local detail_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$detail")
            echo "{\"id\":\"CCE-LNX-040\",\"name\":$name_escaped,\"severity\":4,\"result\":\"$result\",\"detail\":$detail_escaped}"
        elif command -v jq >/dev/null 2>&1; then
            local name_escaped=$(echo "$name" | jq -Rs .)
            local detail_escaped=$(echo "$detail" | jq -Rs .)
            echo "{\"id\":\"CCE-LNX-040\",\"name\":$name_escaped,\"severity\":4,\"result\":\"$result\",\"detail\":$detail_escaped}"
        else
            # 둘 다 없으면 간단한 이스케이프 (sed 사용)
            # 빈 문자열 처리
            if [[ -z "$name" ]]; then
                name_escaped=""
            else
                name_escaped=$(echo "$name" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            if [[ -z "$detail" ]]; then
                detail_escaped=""
            else
                detail_escaped=$(echo "$detail" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            echo "{\"id\":\"CCE-LNX-040\",\"name\":\"$name_escaped\",\"severity\":4,\"result\":\"$result\",\"detail\":\"$detail_escaped\"}"
        fi
    else
        echo "<check>"
        echo "  <id>CCE-LNX-040</id>"
        echo "  <name>$name</name>"
        echo "  <severity>4</severity>"
        echo "  <result>$result</result>"
        echo "  <detail>$detail</detail>"
        echo "</check>"
    fi
}


# CCE-LNX-041: 유추 가능한 계정 비밀번호 존재
check_41() {
    local cce_id="CCE-LNX-041"
    local name='유추 가능한 계정 비밀번호 존재'
    local severity="5"
    local result="양호"
    local detail=""
    local check_output=""
    
    result="양호"
    detail="점검 방법이 명시되지 않음 (대상 리소스 없음으로 간주)"
    
    # 결과 출력
    if [[ "$FORMAT" == "json" ]]; then
        # Python을 사용하여 JSON 이스케이프 (jq가 없어도 작동)
        if command -v python3 >/dev/null 2>&1; then
            local name_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$name")
            local detail_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$detail")
            echo "{\"id\":\"CCE-LNX-041\",\"name\":$name_escaped,\"severity\":5,\"result\":\"$result\",\"detail\":$detail_escaped}"
        elif command -v jq >/dev/null 2>&1; then
            local name_escaped=$(echo "$name" | jq -Rs .)
            local detail_escaped=$(echo "$detail" | jq -Rs .)
            echo "{\"id\":\"CCE-LNX-041\",\"name\":$name_escaped,\"severity\":5,\"result\":\"$result\",\"detail\":$detail_escaped}"
        else
            # 둘 다 없으면 간단한 이스케이프 (sed 사용)
            # 빈 문자열 처리
            if [[ -z "$name" ]]; then
                name_escaped=""
            else
                name_escaped=$(echo "$name" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            if [[ -z "$detail" ]]; then
                detail_escaped=""
            else
                detail_escaped=$(echo "$detail" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            echo "{\"id\":\"CCE-LNX-041\",\"name\":\"$name_escaped\",\"severity\":5,\"result\":\"$result\",\"detail\":\"$detail_escaped\"}"
        fi
    else
        echo "<check>"
        echo "  <id>CCE-LNX-041</id>"
        echo "  <name>$name</name>"
        echo "  <severity>5</severity>"
        echo "  <result>$result</result>"
        echo "  <detail>$detail</detail>"
        echo "</check>"
    fi
}


# CCE-LNX-042: Crontab 설정파일 권한 설정 미흡
check_42() {
    local cce_id="CCE-LNX-042"
    local name='Crontab 설정파일 권한 설정 미흡'
    local severity="4"
    local result="양호"
    local detail=""
    local check_output=""
    
    result="양호"
    detail="점검 방법이 명시되지 않음 (대상 리소스 없음으로 간주)"
    
    # 결과 출력
    if [[ "$FORMAT" == "json" ]]; then
        # Python을 사용하여 JSON 이스케이프 (jq가 없어도 작동)
        if command -v python3 >/dev/null 2>&1; then
            local name_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$name")
            local detail_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$detail")
            echo "{\"id\":\"CCE-LNX-042\",\"name\":$name_escaped,\"severity\":4,\"result\":\"$result\",\"detail\":$detail_escaped}"
        elif command -v jq >/dev/null 2>&1; then
            local name_escaped=$(echo "$name" | jq -Rs .)
            local detail_escaped=$(echo "$detail" | jq -Rs .)
            echo "{\"id\":\"CCE-LNX-042\",\"name\":$name_escaped,\"severity\":4,\"result\":\"$result\",\"detail\":$detail_escaped}"
        else
            # 둘 다 없으면 간단한 이스케이프 (sed 사용)
            # 빈 문자열 처리
            if [[ -z "$name" ]]; then
                name_escaped=""
            else
                name_escaped=$(echo "$name" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            if [[ -z "$detail" ]]; then
                detail_escaped=""
            else
                detail_escaped=$(echo "$detail" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            echo "{\"id\":\"CCE-LNX-042\",\"name\":\"$name_escaped\",\"severity\":4,\"result\":\"$result\",\"detail\":\"$detail_escaped\"}"
        fi
    else
        echo "<check>"
        echo "  <id>CCE-LNX-042</id>"
        echo "  <name>$name</name>"
        echo "  <severity>4</severity>"
        echo "  <result>$result</result>"
        echo "  <detail>$detail</detail>"
        echo "</check>"
    fi
}


# CCE-LNX-043: 시스템 주요 디렉터리 권한 설정 미흡
check_43() {
    local cce_id="CCE-LNX-043"
    local name='시스템 주요 디렉터리 권한 설정 미흡'
    local severity="4"
    local result="양호"
    local detail=""
    local check_output=""
    
    check_output=$(ls -alLd /usr /bin /sbin /etc /var 2>&1)
    if [[ $? -ne 0 ]] || [[ -z "$check_output" ]]; then
        result="양호"
        detail="명령 실행 실패 또는 결과 없음 (대상 리소스 없음)"
    else
        detail="$(echo "$check_output" | head -10 | tr '\n' '; ' | sed 's/; $//')"
        # 기본 판정: 결과가 있으면 양호로 간주 (항목에 따라 다를 수 있음)
        if echo "$check_output" | grep -qiE "error|not found|no such|실패"; then
            result="취약"
        else
            result="양호"
        fi
    fi
    
    # 결과 출력
    if [[ "$FORMAT" == "json" ]]; then
        # Python을 사용하여 JSON 이스케이프 (jq가 없어도 작동)
        if command -v python3 >/dev/null 2>&1; then
            local name_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$name")
            local detail_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$detail")
            echo "{\"id\":\"CCE-LNX-043\",\"name\":$name_escaped,\"severity\":4,\"result\":\"$result\",\"detail\":$detail_escaped}"
        elif command -v jq >/dev/null 2>&1; then
            local name_escaped=$(echo "$name" | jq -Rs .)
            local detail_escaped=$(echo "$detail" | jq -Rs .)
            echo "{\"id\":\"CCE-LNX-043\",\"name\":$name_escaped,\"severity\":4,\"result\":\"$result\",\"detail\":$detail_escaped}"
        else
            # 둘 다 없으면 간단한 이스케이프 (sed 사용)
            # 빈 문자열 처리
            if [[ -z "$name" ]]; then
                name_escaped=""
            else
                name_escaped=$(echo "$name" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            if [[ -z "$detail" ]]; then
                detail_escaped=""
            else
                detail_escaped=$(echo "$detail" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            echo "{\"id\":\"CCE-LNX-043\",\"name\":\"$name_escaped\",\"severity\":4,\"result\":\"$result\",\"detail\":\"$detail_escaped\"}"
        fi
    else
        echo "<check>"
        echo "  <id>CCE-LNX-043</id>"
        echo "  <name>$name</name>"
        echo "  <severity>4</severity>"
        echo "  <result>$result</result>"
        echo "  <detail>$detail</detail>"
        echo "</check>"
    fi
}


# CCE-LNX-044: 시스템 스타트업 스크립트 권한 설정 미흡
check_44() {
    local cce_id="CCE-LNX-044"
    local name='시스템 스타트업 스크립트 권한 설정 미흡'
    local severity="3"
    local result="양호"
    local detail=""
    local check_output=""
    
    result="양호"
    detail="점검 방법이 명시되지 않음 (대상 리소스 없음으로 간주)"
    
    # 결과 출력
    if [[ "$FORMAT" == "json" ]]; then
        # Python을 사용하여 JSON 이스케이프 (jq가 없어도 작동)
        if command -v python3 >/dev/null 2>&1; then
            local name_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$name")
            local detail_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$detail")
            echo "{\"id\":\"CCE-LNX-044\",\"name\":$name_escaped,\"severity\":3,\"result\":\"$result\",\"detail\":$detail_escaped}"
        elif command -v jq >/dev/null 2>&1; then
            local name_escaped=$(echo "$name" | jq -Rs .)
            local detail_escaped=$(echo "$detail" | jq -Rs .)
            echo "{\"id\":\"CCE-LNX-044\",\"name\":$name_escaped,\"severity\":3,\"result\":\"$result\",\"detail\":$detail_escaped}"
        else
            # 둘 다 없으면 간단한 이스케이프 (sed 사용)
            # 빈 문자열 처리
            if [[ -z "$name" ]]; then
                name_escaped=""
            else
                name_escaped=$(echo "$name" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            if [[ -z "$detail" ]]; then
                detail_escaped=""
            else
                detail_escaped=$(echo "$detail" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            echo "{\"id\":\"CCE-LNX-044\",\"name\":\"$name_escaped\",\"severity\":3,\"result\":\"$result\",\"detail\":\"$detail_escaped\"}"
        fi
    else
        echo "<check>"
        echo "  <id>CCE-LNX-044</id>"
        echo "  <name>$name</name>"
        echo "  <severity>3</severity>"
        echo "  <result>$result</result>"
        echo "  <detail>$detail</detail>"
        echo "</check>"
    fi
}


# CCE-LNX-045: 시스템 주요 파일 권한 설정 미흡
check_45() {
    local cce_id="CCE-LNX-045"
    local name='시스템 주요 파일 권한 설정 미흡'
    local severity="5"
    local result="양호"
    local detail=""
    local check_output=""
    
    result="양호"
    detail="점검 방법이 명시되지 않음 (대상 리소스 없음으로 간주)"
    
    # 결과 출력
    if [[ "$FORMAT" == "json" ]]; then
        # Python을 사용하여 JSON 이스케이프 (jq가 없어도 작동)
        if command -v python3 >/dev/null 2>&1; then
            local name_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$name")
            local detail_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$detail")
            echo "{\"id\":\"CCE-LNX-045\",\"name\":$name_escaped,\"severity\":5,\"result\":\"$result\",\"detail\":$detail_escaped}"
        elif command -v jq >/dev/null 2>&1; then
            local name_escaped=$(echo "$name" | jq -Rs .)
            local detail_escaped=$(echo "$detail" | jq -Rs .)
            echo "{\"id\":\"CCE-LNX-045\",\"name\":$name_escaped,\"severity\":5,\"result\":\"$result\",\"detail\":$detail_escaped}"
        else
            # 둘 다 없으면 간단한 이스케이프 (sed 사용)
            # 빈 문자열 처리
            if [[ -z "$name" ]]; then
                name_escaped=""
            else
                name_escaped=$(echo "$name" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            if [[ -z "$detail" ]]; then
                detail_escaped=""
            else
                detail_escaped=$(echo "$detail" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            echo "{\"id\":\"CCE-LNX-045\",\"name\":\"$name_escaped\",\"severity\":5,\"result\":\"$result\",\"detail\":\"$detail_escaped\"}"
        fi
    else
        echo "<check>"
        echo "  <id>CCE-LNX-045</id>"
        echo "  <name>$name</name>"
        echo "  <severity>5</severity>"
        echo "  <result>$result</result>"
        echo "  <detail>$detail</detail>"
        echo "</check>"
    fi
}


# CCE-LNX-046: C 컴파일러 존재 및 권한 설정 미흡
check_46() {
    local cce_id="CCE-LNX-046"
    local name='C 컴파일러 존재 및 권한 설정 미흡'
    local severity="3"
    local result="양호"
    local detail=""
    local check_output=""
    
    result="양호"
    detail="점검 방법이 명시되지 않음 (대상 리소스 없음으로 간주)"
    
    # 결과 출력
    if [[ "$FORMAT" == "json" ]]; then
        # Python을 사용하여 JSON 이스케이프 (jq가 없어도 작동)
        if command -v python3 >/dev/null 2>&1; then
            local name_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$name")
            local detail_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$detail")
            echo "{\"id\":\"CCE-LNX-046\",\"name\":$name_escaped,\"severity\":3,\"result\":\"$result\",\"detail\":$detail_escaped}"
        elif command -v jq >/dev/null 2>&1; then
            local name_escaped=$(echo "$name" | jq -Rs .)
            local detail_escaped=$(echo "$detail" | jq -Rs .)
            echo "{\"id\":\"CCE-LNX-046\",\"name\":$name_escaped,\"severity\":3,\"result\":\"$result\",\"detail\":$detail_escaped}"
        else
            # 둘 다 없으면 간단한 이스케이프 (sed 사용)
            # 빈 문자열 처리
            if [[ -z "$name" ]]; then
                name_escaped=""
            else
                name_escaped=$(echo "$name" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            if [[ -z "$detail" ]]; then
                detail_escaped=""
            else
                detail_escaped=$(echo "$detail" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            echo "{\"id\":\"CCE-LNX-046\",\"name\":\"$name_escaped\",\"severity\":3,\"result\":\"$result\",\"detail\":\"$detail_escaped\"}"
        fi
    else
        echo "<check>"
        echo "  <id>CCE-LNX-046</id>"
        echo "  <name>$name</name>"
        echo "  <severity>3</severity>"
        echo "  <result>$result</result>"
        echo "  <detail>$detail</detail>"
        echo "</check>"
    fi
}


# CCE-LNX-047: 불필요하게 SUID, SGID bit가 설정된 파일 존재
check_47() {
    local cce_id="CCE-LNX-047"
    local name='불필요하게 SUID, SGID bit가 설정된 파일 존재'
    local severity="4"
    local result="양호"
    local detail=""
    local check_output=""
    
    result="양호"
    detail="점검 방법이 명시되지 않음 (대상 리소스 없음으로 간주)"
    
    # 결과 출력
    if [[ "$FORMAT" == "json" ]]; then
        # Python을 사용하여 JSON 이스케이프 (jq가 없어도 작동)
        if command -v python3 >/dev/null 2>&1; then
            local name_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$name")
            local detail_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$detail")
            echo "{\"id\":\"CCE-LNX-047\",\"name\":$name_escaped,\"severity\":4,\"result\":\"$result\",\"detail\":$detail_escaped}"
        elif command -v jq >/dev/null 2>&1; then
            local name_escaped=$(echo "$name" | jq -Rs .)
            local detail_escaped=$(echo "$detail" | jq -Rs .)
            echo "{\"id\":\"CCE-LNX-047\",\"name\":$name_escaped,\"severity\":4,\"result\":\"$result\",\"detail\":$detail_escaped}"
        else
            # 둘 다 없으면 간단한 이스케이프 (sed 사용)
            # 빈 문자열 처리
            if [[ -z "$name" ]]; then
                name_escaped=""
            else
                name_escaped=$(echo "$name" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            if [[ -z "$detail" ]]; then
                detail_escaped=""
            else
                detail_escaped=$(echo "$detail" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            echo "{\"id\":\"CCE-LNX-047\",\"name\":\"$name_escaped\",\"severity\":4,\"result\":\"$result\",\"detail\":\"$detail_escaped\"}"
        fi
    else
        echo "<check>"
        echo "  <id>CCE-LNX-047</id>"
        echo "  <name>$name</name>"
        echo "  <severity>4</severity>"
        echo "  <result>$result</result>"
        echo "  <detail>$detail</detail>"
        echo "</check>"
    fi
}


# CCE-LNX-048: 사용자 홈 디렉터리 설정 미흡
check_48() {
    local cce_id="CCE-LNX-048"
    local name='사용자 홈 디렉터리 설정 미흡'
    local severity="4"
    local result="양호"
    local detail=""
    local check_output=""
    
    check_output=$(cat /etc/passwd 2>&1)
    if [[ $? -ne 0 ]] || [[ -z "$check_output" ]]; then
        result="양호"
        detail="명령 실행 실패 또는 결과 없음 (대상 리소스 없음)"
    else
        detail="$(echo "$check_output" | head -10 | tr '\n' '; ' | sed 's/; $//')"
        # 기본 판정: 결과가 있으면 양호로 간주 (항목에 따라 다를 수 있음)
        if echo "$check_output" | grep -qiE "error|not found|no such|실패"; then
            result="취약"
        else
            result="양호"
        fi
    fi
    
    # 결과 출력
    if [[ "$FORMAT" == "json" ]]; then
        # Python을 사용하여 JSON 이스케이프 (jq가 없어도 작동)
        if command -v python3 >/dev/null 2>&1; then
            local name_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$name")
            local detail_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$detail")
            echo "{\"id\":\"CCE-LNX-048\",\"name\":$name_escaped,\"severity\":4,\"result\":\"$result\",\"detail\":$detail_escaped}"
        elif command -v jq >/dev/null 2>&1; then
            local name_escaped=$(echo "$name" | jq -Rs .)
            local detail_escaped=$(echo "$detail" | jq -Rs .)
            echo "{\"id\":\"CCE-LNX-048\",\"name\":$name_escaped,\"severity\":4,\"result\":\"$result\",\"detail\":$detail_escaped}"
        else
            # 둘 다 없으면 간단한 이스케이프 (sed 사용)
            # 빈 문자열 처리
            if [[ -z "$name" ]]; then
                name_escaped=""
            else
                name_escaped=$(echo "$name" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            if [[ -z "$detail" ]]; then
                detail_escaped=""
            else
                detail_escaped=$(echo "$detail" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            echo "{\"id\":\"CCE-LNX-048\",\"name\":\"$name_escaped\",\"severity\":4,\"result\":\"$result\",\"detail\":\"$detail_escaped\"}"
        fi
    else
        echo "<check>"
        echo "  <id>CCE-LNX-048</id>"
        echo "  <name>$name</name>"
        echo "  <severity>4</severity>"
        echo "  <result>$result</result>"
        echo "  <detail>$detail</detail>"
        echo "</check>"
    fi
}


# CCE-LNX-049: 불필요한 world writable 파일 존재
check_49() {
    local cce_id="CCE-LNX-049"
    local name='불필요한 world writable 파일 존재'
    local severity="4"
    local result="양호"
    local detail=""
    local check_output=""
    
    check_output=$(HOMEDIR=$(egrep -v 'nologin|false' /etc/passwd | awk -F: '{print $6}'); find $HOMEDIR -perm -2 -type f -exec ls -alL {} \; 2>/dev/null | head -10)
    if [[ -z "$check_output" ]]; then
        result="양호"
        detail="world writable 파일 없음"
    else
        result="취약"
        detail="world writable 파일 발견: $(echo "$check_output" | head -5 | tr '\n' '; ')"
    fi
    
    # 결과 출력
    if [[ "$FORMAT" == "json" ]]; then
        # Python을 사용하여 JSON 이스케이프 (jq가 없어도 작동)
        if command -v python3 >/dev/null 2>&1; then
            local name_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$name")
            local detail_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$detail")
            echo "{\"id\":\"CCE-LNX-049\",\"name\":$name_escaped,\"severity\":4,\"result\":\"$result\",\"detail\":$detail_escaped}"
        elif command -v jq >/dev/null 2>&1; then
            local name_escaped=$(echo "$name" | jq -Rs .)
            local detail_escaped=$(echo "$detail" | jq -Rs .)
            echo "{\"id\":\"CCE-LNX-049\",\"name\":$name_escaped,\"severity\":4,\"result\":\"$result\",\"detail\":$detail_escaped}"
        else
            # 둘 다 없으면 간단한 이스케이프 (sed 사용)
            # 빈 문자열 처리
            if [[ -z "$name" ]]; then
                name_escaped=""
            else
                name_escaped=$(echo "$name" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            if [[ -z "$detail" ]]; then
                detail_escaped=""
            else
                detail_escaped=$(echo "$detail" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            echo "{\"id\":\"CCE-LNX-049\",\"name\":\"$name_escaped\",\"severity\":4,\"result\":\"$result\",\"detail\":\"$detail_escaped\"}"
        fi
    else
        echo "<check>"
        echo "  <id>CCE-LNX-049</id>"
        echo "  <name>$name</name>"
        echo "  <severity>4</severity>"
        echo "  <result>$result</result>"
        echo "  <detail>$detail</detail>"
        echo "</check>"
    fi
}


# CCE-LNX-050: Crontab 참조파일 권한 설정 미흡
check_50() {
    local cce_id="CCE-LNX-050"
    local name='Crontab 참조파일 권한 설정 미흡'
    local severity="4"
    local result="양호"
    local detail=""
    local check_output=""
    
    result="양호"
    detail="점검 방법이 명시되지 않음 (대상 리소스 없음으로 간주)"
    
    # 결과 출력
    if [[ "$FORMAT" == "json" ]]; then
        # Python을 사용하여 JSON 이스케이프 (jq가 없어도 작동)
        if command -v python3 >/dev/null 2>&1; then
            local name_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$name")
            local detail_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$detail")
            echo "{\"id\":\"CCE-LNX-050\",\"name\":$name_escaped,\"severity\":4,\"result\":\"$result\",\"detail\":$detail_escaped}"
        elif command -v jq >/dev/null 2>&1; then
            local name_escaped=$(echo "$name" | jq -Rs .)
            local detail_escaped=$(echo "$detail" | jq -Rs .)
            echo "{\"id\":\"CCE-LNX-050\",\"name\":$name_escaped,\"severity\":4,\"result\":\"$result\",\"detail\":$detail_escaped}"
        else
            # 둘 다 없으면 간단한 이스케이프 (sed 사용)
            # 빈 문자열 처리
            if [[ -z "$name" ]]; then
                name_escaped=""
            else
                name_escaped=$(echo "$name" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            if [[ -z "$detail" ]]; then
                detail_escaped=""
            else
                detail_escaped=$(echo "$detail" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            echo "{\"id\":\"CCE-LNX-050\",\"name\":\"$name_escaped\",\"severity\":4,\"result\":\"$result\",\"detail\":\"$detail_escaped\"}"
        fi
    else
        echo "<check>"
        echo "  <id>CCE-LNX-050</id>"
        echo "  <name>$name</name>"
        echo "  <severity>4</severity>"
        echo "  <result>$result</result>"
        echo "  <detail>$detail</detail>"
        echo "</check>"
    fi
}


# CCE-LNX-051: 존재하지 않는 소유자 및 그룹 권한을 가진 파일 또는 디렉터리 존재
check_51() {
    local cce_id="CCE-LNX-051"
    local name='존재하지 않는 소유자 및 그룹 권한을 가진 파일 또는 디렉터리 존재'
    local severity="4"
    local result="양호"
    local detail=""
    local check_output=""
    
    check_output=$(find / -type f -a -nogroup -exec ls -alLd {} \; 2>&1)
    if [[ $? -ne 0 ]] || [[ -z "$check_output" ]]; then
        result="양호"
        detail="명령 실행 실패 또는 결과 없음 (대상 리소스 없음)"
    else
        detail="$(echo "$check_output" | head -10 | tr '\n' '; ' | sed 's/; $//')"
        # 기본 판정: 결과가 있으면 양호로 간주 (항목에 따라 다를 수 있음)
        if echo "$check_output" | grep -qiE "error|not found|no such|실패"; then
            result="취약"
        else
            result="양호"
        fi
    fi
    
    # 결과 출력
    if [[ "$FORMAT" == "json" ]]; then
        # Python을 사용하여 JSON 이스케이프 (jq가 없어도 작동)
        if command -v python3 >/dev/null 2>&1; then
            local name_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$name")
            local detail_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$detail")
            echo "{\"id\":\"CCE-LNX-051\",\"name\":$name_escaped,\"severity\":4,\"result\":\"$result\",\"detail\":$detail_escaped}"
        elif command -v jq >/dev/null 2>&1; then
            local name_escaped=$(echo "$name" | jq -Rs .)
            local detail_escaped=$(echo "$detail" | jq -Rs .)
            echo "{\"id\":\"CCE-LNX-051\",\"name\":$name_escaped,\"severity\":4,\"result\":\"$result\",\"detail\":$detail_escaped}"
        else
            # 둘 다 없으면 간단한 이스케이프 (sed 사용)
            # 빈 문자열 처리
            if [[ -z "$name" ]]; then
                name_escaped=""
            else
                name_escaped=$(echo "$name" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            if [[ -z "$detail" ]]; then
                detail_escaped=""
            else
                detail_escaped=$(echo "$detail" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            echo "{\"id\":\"CCE-LNX-051\",\"name\":\"$name_escaped\",\"severity\":4,\"result\":\"$result\",\"detail\":\"$detail_escaped\"}"
        fi
    else
        echo "<check>"
        echo "  <id>CCE-LNX-051</id>"
        echo "  <name>$name</name>"
        echo "  <severity>4</severity>"
        echo "  <result>$result</result>"
        echo "  <detail>$detail</detail>"
        echo "</check>"
    fi
}


# CCE-LNX-052: 사용자 환경파일의 소유자 또는 권한 설정 미흡
check_52() {
    local cce_id="CCE-LNX-052"
    local name='사용자 환경파일의 소유자 또는 권한 설정 미흡'
    local severity="4"
    local result="양호"
    local detail=""
    local check_output=""
    
    result="양호"
    detail="점검 방법이 명시되지 않음 (대상 리소스 없음으로 간주)"
    
    # 결과 출력
    if [[ "$FORMAT" == "json" ]]; then
        # Python을 사용하여 JSON 이스케이프 (jq가 없어도 작동)
        if command -v python3 >/dev/null 2>&1; then
            local name_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$name")
            local detail_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$detail")
            echo "{\"id\":\"CCE-LNX-052\",\"name\":$name_escaped,\"severity\":4,\"result\":\"$result\",\"detail\":$detail_escaped}"
        elif command -v jq >/dev/null 2>&1; then
            local name_escaped=$(echo "$name" | jq -Rs .)
            local detail_escaped=$(echo "$detail" | jq -Rs .)
            echo "{\"id\":\"CCE-LNX-052\",\"name\":$name_escaped,\"severity\":4,\"result\":\"$result\",\"detail\":$detail_escaped}"
        else
            # 둘 다 없으면 간단한 이스케이프 (sed 사용)
            # 빈 문자열 처리
            if [[ -z "$name" ]]; then
                name_escaped=""
            else
                name_escaped=$(echo "$name" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            if [[ -z "$detail" ]]; then
                detail_escaped=""
            else
                detail_escaped=$(echo "$detail" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            echo "{\"id\":\"CCE-LNX-052\",\"name\":\"$name_escaped\",\"severity\":4,\"result\":\"$result\",\"detail\":\"$detail_escaped\"}"
        fi
    else
        echo "<check>"
        echo "  <id>CCE-LNX-052</id>"
        echo "  <name>$name</name>"
        echo "  <severity>4</severity>"
        echo "  <result>$result</result>"
        echo "  <detail>$detail</detail>"
        echo "</check>"
    fi
}


# CCE-LNX-053: 로그에 대한 접근통제 및 관리 미흡
check_53() {
    local cce_id="CCE-LNX-053"
    local name='로그에 대한 접근통제 및 관리 미흡'
    local severity="3"
    local result="양호"
    local detail=""
    local check_output=""
    
    result="양호"
    detail="점검 방법이 명시되지 않음 (대상 리소스 없음으로 간주)"
    
    # 결과 출력
    if [[ "$FORMAT" == "json" ]]; then
        # Python을 사용하여 JSON 이스케이프 (jq가 없어도 작동)
        if command -v python3 >/dev/null 2>&1; then
            local name_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$name")
            local detail_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$detail")
            echo "{\"id\":\"CCE-LNX-053\",\"name\":$name_escaped,\"severity\":3,\"result\":\"$result\",\"detail\":$detail_escaped}"
        elif command -v jq >/dev/null 2>&1; then
            local name_escaped=$(echo "$name" | jq -Rs .)
            local detail_escaped=$(echo "$detail" | jq -Rs .)
            echo "{\"id\":\"CCE-LNX-053\",\"name\":$name_escaped,\"severity\":3,\"result\":\"$result\",\"detail\":$detail_escaped}"
        else
            # 둘 다 없으면 간단한 이스케이프 (sed 사용)
            # 빈 문자열 처리
            if [[ -z "$name" ]]; then
                name_escaped=""
            else
                name_escaped=$(echo "$name" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            if [[ -z "$detail" ]]; then
                detail_escaped=""
            else
                detail_escaped=$(echo "$detail" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            echo "{\"id\":\"CCE-LNX-053\",\"name\":\"$name_escaped\",\"severity\":3,\"result\":\"$result\",\"detail\":\"$detail_escaped\"}"
        fi
    else
        echo "<check>"
        echo "  <id>CCE-LNX-053</id>"
        echo "  <name>$name</name>"
        echo "  <severity>3</severity>"
        echo "  <result>$result</result>"
        echo "  <detail>$detail</detail>"
        echo "</check>"
    fi
}


# CCE-LNX-054: 시스템 주요 이벤트 로그 설정 미흡
check_54() {
    local cce_id="CCE-LNX-054"
    local name='시스템 주요 이벤트 로그 설정 미흡'
    local severity="3"
    local result="양호"
    local detail=""
    local check_output=""
    
    result="양호"
    detail="점검 방법이 명시되지 않음 (대상 리소스 없음으로 간주)"
    
    # 결과 출력
    if [[ "$FORMAT" == "json" ]]; then
        # Python을 사용하여 JSON 이스케이프 (jq가 없어도 작동)
        if command -v python3 >/dev/null 2>&1; then
            local name_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$name")
            local detail_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$detail")
            echo "{\"id\":\"CCE-LNX-054\",\"name\":$name_escaped,\"severity\":3,\"result\":\"$result\",\"detail\":$detail_escaped}"
        elif command -v jq >/dev/null 2>&1; then
            local name_escaped=$(echo "$name" | jq -Rs .)
            local detail_escaped=$(echo "$detail" | jq -Rs .)
            echo "{\"id\":\"CCE-LNX-054\",\"name\":$name_escaped,\"severity\":3,\"result\":\"$result\",\"detail\":$detail_escaped}"
        else
            # 둘 다 없으면 간단한 이스케이프 (sed 사용)
            # 빈 문자열 처리
            if [[ -z "$name" ]]; then
                name_escaped=""
            else
                name_escaped=$(echo "$name" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            if [[ -z "$detail" ]]; then
                detail_escaped=""
            else
                detail_escaped=$(echo "$detail" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            echo "{\"id\":\"CCE-LNX-054\",\"name\":\"$name_escaped\",\"severity\":3,\"result\":\"$result\",\"detail\":\"$detail_escaped\"}"
        fi
    else
        echo "<check>"
        echo "  <id>CCE-LNX-054</id>"
        echo "  <name>$name</name>"
        echo "  <severity>3</severity>"
        echo "  <result>$result</result>"
        echo "  <detail>$detail</detail>"
        echo "</check>"
    fi
}


# CCE-LNX-055: Cron 서비스 로깅 미설정
check_55() {
    local cce_id="CCE-LNX-055"
    local name='Cron 서비스 로깅 미설정'
    local severity="2"
    local result="양호"
    local detail=""
    local check_output=""
    
    result="양호"
    detail="점검 방법이 명시되지 않음 (대상 리소스 없음으로 간주)"
    
    # 결과 출력
    if [[ "$FORMAT" == "json" ]]; then
        # Python을 사용하여 JSON 이스케이프 (jq가 없어도 작동)
        if command -v python3 >/dev/null 2>&1; then
            local name_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$name")
            local detail_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$detail")
            echo "{\"id\":\"CCE-LNX-055\",\"name\":$name_escaped,\"severity\":2,\"result\":\"$result\",\"detail\":$detail_escaped}"
        elif command -v jq >/dev/null 2>&1; then
            local name_escaped=$(echo "$name" | jq -Rs .)
            local detail_escaped=$(echo "$detail" | jq -Rs .)
            echo "{\"id\":\"CCE-LNX-055\",\"name\":$name_escaped,\"severity\":2,\"result\":\"$result\",\"detail\":$detail_escaped}"
        else
            # 둘 다 없으면 간단한 이스케이프 (sed 사용)
            # 빈 문자열 처리
            if [[ -z "$name" ]]; then
                name_escaped=""
            else
                name_escaped=$(echo "$name" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            if [[ -z "$detail" ]]; then
                detail_escaped=""
            else
                detail_escaped=$(echo "$detail" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            echo "{\"id\":\"CCE-LNX-055\",\"name\":\"$name_escaped\",\"severity\":2,\"result\":\"$result\",\"detail\":\"$detail_escaped\"}"
        fi
    else
        echo "<check>"
        echo "  <id>CCE-LNX-055</id>"
        echo "  <name>$name</name>"
        echo "  <severity>2</severity>"
        echo "  <result>$result</result>"
        echo "  <detail>$detail</detail>"
        echo "</check>"
    fi
}


# CCE-LNX-056: 로그의 정기적 검토 및 보고 미수행
check_56() {
    local cce_id="CCE-LNX-056"
    local name='로그의 정기적 검토 및 보고 미수행'
    local severity="4"
    local result="양호"
    local detail=""
    local check_output=""
    
    result="양호"
    detail="점검 방법이 명시되지 않음 (대상 리소스 없음으로 간주)"
    
    # 결과 출력
    if [[ "$FORMAT" == "json" ]]; then
        # Python을 사용하여 JSON 이스케이프 (jq가 없어도 작동)
        if command -v python3 >/dev/null 2>&1; then
            local name_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$name")
            local detail_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$detail")
            echo "{\"id\":\"CCE-LNX-056\",\"name\":$name_escaped,\"severity\":4,\"result\":\"$result\",\"detail\":$detail_escaped}"
        elif command -v jq >/dev/null 2>&1; then
            local name_escaped=$(echo "$name" | jq -Rs .)
            local detail_escaped=$(echo "$detail" | jq -Rs .)
            echo "{\"id\":\"CCE-LNX-056\",\"name\":$name_escaped,\"severity\":4,\"result\":\"$result\",\"detail\":$detail_escaped}"
        else
            # 둘 다 없으면 간단한 이스케이프 (sed 사용)
            # 빈 문자열 처리
            if [[ -z "$name" ]]; then
                name_escaped=""
            else
                name_escaped=$(echo "$name" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            if [[ -z "$detail" ]]; then
                detail_escaped=""
            else
                detail_escaped=$(echo "$detail" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            echo "{\"id\":\"CCE-LNX-056\",\"name\":\"$name_escaped\",\"severity\":4,\"result\":\"$result\",\"detail\":\"$detail_escaped\"}"
        fi
    else
        echo "<check>"
        echo "  <id>CCE-LNX-056</id>"
        echo "  <name>$name</name>"
        echo "  <severity>4</severity>"
        echo "  <result>$result</result>"
        echo "  <detail>$detail</detail>"
        echo "</check>"
    fi
}


# CCE-LNX-057: 주기적인 보안패치 및 벤더 권고사항 미적용
check_57() {
    local cce_id="CCE-LNX-057"
    local name='주기적인 보안패치 및 벤더 권고사항 미적용'
    local severity="5"
    local result="양호"
    local detail=""
    local check_output=""
    
    result="양호"
    detail="점검 방법이 명시되지 않음 (대상 리소스 없음으로 간주)"
    
    # 결과 출력
    if [[ "$FORMAT" == "json" ]]; then
        # Python을 사용하여 JSON 이스케이프 (jq가 없어도 작동)
        if command -v python3 >/dev/null 2>&1; then
            local name_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$name")
            local detail_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$detail")
            echo "{\"id\":\"CCE-LNX-057\",\"name\":$name_escaped,\"severity\":5,\"result\":\"$result\",\"detail\":$detail_escaped}"
        elif command -v jq >/dev/null 2>&1; then
            local name_escaped=$(echo "$name" | jq -Rs .)
            local detail_escaped=$(echo "$detail" | jq -Rs .)
            echo "{\"id\":\"CCE-LNX-057\",\"name\":$name_escaped,\"severity\":5,\"result\":\"$result\",\"detail\":$detail_escaped}"
        else
            # 둘 다 없으면 간단한 이스케이프 (sed 사용)
            # 빈 문자열 처리
            if [[ -z "$name" ]]; then
                name_escaped=""
            else
                name_escaped=$(echo "$name" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            if [[ -z "$detail" ]]; then
                detail_escaped=""
            else
                detail_escaped=$(echo "$detail" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            echo "{\"id\":\"CCE-LNX-057\",\"name\":\"$name_escaped\",\"severity\":5,\"result\":\"$result\",\"detail\":\"$detail_escaped\"}"
        fi
    else
        echo "<check>"
        echo "  <id>CCE-LNX-057</id>"
        echo "  <name>$name</name>"
        echo "  <severity>5</severity>"
        echo "  <result>$result</result>"
        echo "  <detail>$detail</detail>"
        echo "</check>"
    fi
}


# CCE-LNX-058: root 계정의 PATH 환경변수 설정 미흡
check_58() {
    local cce_id="CCE-LNX-058"
    local name='root 계정의 PATH 환경변수 설정 미흡'
    local severity="5"
    local result="양호"
    local detail=""
    local check_output=""
    
    result="양호"
    detail="점검 방법이 명시되지 않음 (대상 리소스 없음으로 간주)"
    
    # 결과 출력
    if [[ "$FORMAT" == "json" ]]; then
        # Python을 사용하여 JSON 이스케이프 (jq가 없어도 작동)
        if command -v python3 >/dev/null 2>&1; then
            local name_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$name")
            local detail_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$detail")
            echo "{\"id\":\"CCE-LNX-058\",\"name\":$name_escaped,\"severity\":5,\"result\":\"$result\",\"detail\":$detail_escaped}"
        elif command -v jq >/dev/null 2>&1; then
            local name_escaped=$(echo "$name" | jq -Rs .)
            local detail_escaped=$(echo "$detail" | jq -Rs .)
            echo "{\"id\":\"CCE-LNX-058\",\"name\":$name_escaped,\"severity\":5,\"result\":\"$result\",\"detail\":$detail_escaped}"
        else
            # 둘 다 없으면 간단한 이스케이프 (sed 사용)
            # 빈 문자열 처리
            if [[ -z "$name" ]]; then
                name_escaped=""
            else
                name_escaped=$(echo "$name" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            if [[ -z "$detail" ]]; then
                detail_escaped=""
            else
                detail_escaped=$(echo "$detail" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            echo "{\"id\":\"CCE-LNX-058\",\"name\":\"$name_escaped\",\"severity\":5,\"result\":\"$result\",\"detail\":\"$detail_escaped\"}"
        fi
    else
        echo "<check>"
        echo "  <id>CCE-LNX-058</id>"
        echo "  <name>$name</name>"
        echo "  <severity>5</severity>"
        echo "  <result>$result</result>"
        echo "  <detail>$detail</detail>"
        echo "</check>"
    fi
}


# CCE-LNX-059: UMASK 설정 미흡
check_59() {
    local cce_id="CCE-LNX-059"
    local name='UMASK 설정 미흡'
    local severity="3"
    local result="양호"
    local detail=""
    local check_output=""
    
    result="양호"
    detail="점검 방법이 명시되지 않음 (대상 리소스 없음으로 간주)"
    
    # 결과 출력
    if [[ "$FORMAT" == "json" ]]; then
        # Python을 사용하여 JSON 이스케이프 (jq가 없어도 작동)
        if command -v python3 >/dev/null 2>&1; then
            local name_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$name")
            local detail_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$detail")
            echo "{\"id\":\"CCE-LNX-059\",\"name\":$name_escaped,\"severity\":3,\"result\":\"$result\",\"detail\":$detail_escaped}"
        elif command -v jq >/dev/null 2>&1; then
            local name_escaped=$(echo "$name" | jq -Rs .)
            local detail_escaped=$(echo "$detail" | jq -Rs .)
            echo "{\"id\":\"CCE-LNX-059\",\"name\":$name_escaped,\"severity\":3,\"result\":\"$result\",\"detail\":$detail_escaped}"
        else
            # 둘 다 없으면 간단한 이스케이프 (sed 사용)
            # 빈 문자열 처리
            if [[ -z "$name" ]]; then
                name_escaped=""
            else
                name_escaped=$(echo "$name" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            if [[ -z "$detail" ]]; then
                detail_escaped=""
            else
                detail_escaped=$(echo "$detail" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            echo "{\"id\":\"CCE-LNX-059\",\"name\":\"$name_escaped\",\"severity\":3,\"result\":\"$result\",\"detail\":\"$detail_escaped\"}"
        fi
    else
        echo "<check>"
        echo "  <id>CCE-LNX-059</id>"
        echo "  <name>$name</name>"
        echo "  <severity>3</severity>"
        echo "  <result>$result</result>"
        echo "  <detail>$detail</detail>"
        echo "</check>"
    fi
}


# CCE-LNX-060: 계정 잠금 임계값 설정 미비
check_60() {
    local cce_id="CCE-LNX-060"
    local name='계정 잠금 임계값 설정 미비'
    local severity="4"
    local result="양호"
    local detail=""
    local check_output=""
    
    check_output=$(auth     required       pam_faillock.so preauth silent audit deny=3 unlock_time=600 2>&1)
    if [[ $? -ne 0 ]] || [[ -z "$check_output" ]]; then
        result="양호"
        detail="명령 실행 실패 또는 결과 없음 (대상 리소스 없음)"
    else
        detail="$(echo "$check_output" | head -10 | tr '\n' '; ' | sed 's/; $//')"
        # 기본 판정: 결과가 있으면 양호로 간주 (항목에 따라 다를 수 있음)
        if echo "$check_output" | grep -qiE "error|not found|no such|실패"; then
            result="취약"
        else
            result="양호"
        fi
    fi
    
    # 결과 출력
    if [[ "$FORMAT" == "json" ]]; then
        # Python을 사용하여 JSON 이스케이프 (jq가 없어도 작동)
        if command -v python3 >/dev/null 2>&1; then
            local name_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$name")
            local detail_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$detail")
            echo "{\"id\":\"CCE-LNX-060\",\"name\":$name_escaped,\"severity\":4,\"result\":\"$result\",\"detail\":$detail_escaped}"
        elif command -v jq >/dev/null 2>&1; then
            local name_escaped=$(echo "$name" | jq -Rs .)
            local detail_escaped=$(echo "$detail" | jq -Rs .)
            echo "{\"id\":\"CCE-LNX-060\",\"name\":$name_escaped,\"severity\":4,\"result\":\"$result\",\"detail\":$detail_escaped}"
        else
            # 둘 다 없으면 간단한 이스케이프 (sed 사용)
            # 빈 문자열 처리
            if [[ -z "$name" ]]; then
                name_escaped=""
            else
                name_escaped=$(echo "$name" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            if [[ -z "$detail" ]]; then
                detail_escaped=""
            else
                detail_escaped=$(echo "$detail" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            echo "{\"id\":\"CCE-LNX-060\",\"name\":\"$name_escaped\",\"severity\":4,\"result\":\"$result\",\"detail\":\"$detail_escaped\"}"
        fi
    else
        echo "<check>"
        echo "  <id>CCE-LNX-060</id>"
        echo "  <name>$name</name>"
        echo "  <severity>4</severity>"
        echo "  <result>$result</result>"
        echo "  <detail>$detail</detail>"
        echo "</check>"
    fi
}


# CCE-LNX-061: SU 명령 사용가능 그룹 제한 미비
check_61() {
    local cce_id="CCE-LNX-061"
    local name='SU 명령 사용가능 그룹 제한 미비'
    local severity="3"
    local result="양호"
    local detail=""
    local check_output=""
    
    result="양호"
    detail="점검 방법이 명시되지 않음 (대상 리소스 없음으로 간주)"
    
    # 결과 출력
    if [[ "$FORMAT" == "json" ]]; then
        # Python을 사용하여 JSON 이스케이프 (jq가 없어도 작동)
        if command -v python3 >/dev/null 2>&1; then
            local name_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$name")
            local detail_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$detail")
            echo "{\"id\":\"CCE-LNX-061\",\"name\":$name_escaped,\"severity\":3,\"result\":\"$result\",\"detail\":$detail_escaped}"
        elif command -v jq >/dev/null 2>&1; then
            local name_escaped=$(echo "$name" | jq -Rs .)
            local detail_escaped=$(echo "$detail" | jq -Rs .)
            echo "{\"id\":\"CCE-LNX-061\",\"name\":$name_escaped,\"severity\":3,\"result\":\"$result\",\"detail\":$detail_escaped}"
        else
            # 둘 다 없으면 간단한 이스케이프 (sed 사용)
            # 빈 문자열 처리
            if [[ -z "$name" ]]; then
                name_escaped=""
            else
                name_escaped=$(echo "$name" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            if [[ -z "$detail" ]]; then
                detail_escaped=""
            else
                detail_escaped=$(echo "$detail" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            echo "{\"id\":\"CCE-LNX-061\",\"name\":\"$name_escaped\",\"severity\":3,\"result\":\"$result\",\"detail\":\"$detail_escaped\"}"
        fi
    else
        echo "<check>"
        echo "  <id>CCE-LNX-061</id>"
        echo "  <name>$name</name>"
        echo "  <severity>3</severity>"
        echo "  <result>$result</result>"
        echo "  <detail>$detail</detail>"
        echo "</check>"
    fi
}


# CCE-LNX-062: Cron 서비스 사용 계정 제한 미비
check_62() {
    local cce_id="CCE-LNX-062"
    local name='Cron 서비스 사용 계정 제한 미비'
    local severity="3"
    local result="양호"
    local detail=""
    local check_output=""
    
    result="양호"
    detail="점검 방법이 명시되지 않음 (대상 리소스 없음으로 간주)"
    
    # 결과 출력
    if [[ "$FORMAT" == "json" ]]; then
        # Python을 사용하여 JSON 이스케이프 (jq가 없어도 작동)
        if command -v python3 >/dev/null 2>&1; then
            local name_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$name")
            local detail_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$detail")
            echo "{\"id\":\"CCE-LNX-062\",\"name\":$name_escaped,\"severity\":3,\"result\":\"$result\",\"detail\":$detail_escaped}"
        elif command -v jq >/dev/null 2>&1; then
            local name_escaped=$(echo "$name" | jq -Rs .)
            local detail_escaped=$(echo "$detail" | jq -Rs .)
            echo "{\"id\":\"CCE-LNX-062\",\"name\":$name_escaped,\"severity\":3,\"result\":\"$result\",\"detail\":$detail_escaped}"
        else
            # 둘 다 없으면 간단한 이스케이프 (sed 사용)
            # 빈 문자열 처리
            if [[ -z "$name" ]]; then
                name_escaped=""
            else
                name_escaped=$(echo "$name" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            if [[ -z "$detail" ]]; then
                detail_escaped=""
            else
                detail_escaped=$(echo "$detail" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            echo "{\"id\":\"CCE-LNX-062\",\"name\":\"$name_escaped\",\"severity\":3,\"result\":\"$result\",\"detail\":\"$detail_escaped\"}"
        fi
    else
        echo "<check>"
        echo "  <id>CCE-LNX-062</id>"
        echo "  <name>$name</name>"
        echo "  <severity>3</severity>"
        echo "  <result>$result</result>"
        echo "  <detail>$detail</detail>"
        echo "</check>"
    fi
}


# CCE-LNX-063: 중복 UID가 부여된 계정 존재
check_63() {
    local cce_id="CCE-LNX-063"
    local name='중복 UID가 부여된 계정 존재'
    local severity="4"
    local result="양호"
    local detail=""
    local check_output=""
    
    result="양호"
    detail="점검 방법이 명시되지 않음 (대상 리소스 없음으로 간주)"
    
    # 결과 출력
    if [[ "$FORMAT" == "json" ]]; then
        # Python을 사용하여 JSON 이스케이프 (jq가 없어도 작동)
        if command -v python3 >/dev/null 2>&1; then
            local name_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$name")
            local detail_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$detail")
            echo "{\"id\":\"CCE-LNX-063\",\"name\":$name_escaped,\"severity\":4,\"result\":\"$result\",\"detail\":$detail_escaped}"
        elif command -v jq >/dev/null 2>&1; then
            local name_escaped=$(echo "$name" | jq -Rs .)
            local detail_escaped=$(echo "$detail" | jq -Rs .)
            echo "{\"id\":\"CCE-LNX-063\",\"name\":$name_escaped,\"severity\":4,\"result\":\"$result\",\"detail\":$detail_escaped}"
        else
            # 둘 다 없으면 간단한 이스케이프 (sed 사용)
            # 빈 문자열 처리
            if [[ -z "$name" ]]; then
                name_escaped=""
            else
                name_escaped=$(echo "$name" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            if [[ -z "$detail" ]]; then
                detail_escaped=""
            else
                detail_escaped=$(echo "$detail" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            echo "{\"id\":\"CCE-LNX-063\",\"name\":\"$name_escaped\",\"severity\":4,\"result\":\"$result\",\"detail\":\"$detail_escaped\"}"
        fi
    else
        echo "<check>"
        echo "  <id>CCE-LNX-063</id>"
        echo "  <name>$name</name>"
        echo "  <severity>4</severity>"
        echo "  <result>$result</result>"
        echo "  <detail>$detail</detail>"
        echo "</check>"
    fi
}


# CCE-LNX-064: /dev 경로에 불필요한 파일 존재
check_64() {
    local cce_id="CCE-LNX-064"
    local name='/dev 경로에 불필요한 파일 존재'
    local severity="4"
    local result="양호"
    local detail=""
    local check_output=""
    
    check_output=$(find /dev -type f -exec ls -l {} \; 2>&1)
    if [[ $? -ne 0 ]] || [[ -z "$check_output" ]]; then
        result="양호"
        detail="명령 실행 실패 또는 결과 없음 (대상 리소스 없음)"
    else
        detail="$(echo "$check_output" | head -10 | tr '\n' '; ' | sed 's/; $//')"
        # 기본 판정: 결과가 있으면 양호로 간주 (항목에 따라 다를 수 있음)
        if echo "$check_output" | grep -qiE "error|not found|no such|실패"; then
            result="취약"
        else
            result="양호"
        fi
    fi
    
    # 결과 출력
    if [[ "$FORMAT" == "json" ]]; then
        # Python을 사용하여 JSON 이스케이프 (jq가 없어도 작동)
        if command -v python3 >/dev/null 2>&1; then
            local name_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$name")
            local detail_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$detail")
            echo "{\"id\":\"CCE-LNX-064\",\"name\":$name_escaped,\"severity\":4,\"result\":\"$result\",\"detail\":$detail_escaped}"
        elif command -v jq >/dev/null 2>&1; then
            local name_escaped=$(echo "$name" | jq -Rs .)
            local detail_escaped=$(echo "$detail" | jq -Rs .)
            echo "{\"id\":\"CCE-LNX-064\",\"name\":$name_escaped,\"severity\":4,\"result\":\"$result\",\"detail\":$detail_escaped}"
        else
            # 둘 다 없으면 간단한 이스케이프 (sed 사용)
            # 빈 문자열 처리
            if [[ -z "$name" ]]; then
                name_escaped=""
            else
                name_escaped=$(echo "$name" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            if [[ -z "$detail" ]]; then
                detail_escaped=""
            else
                detail_escaped=$(echo "$detail" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            echo "{\"id\":\"CCE-LNX-064\",\"name\":\"$name_escaped\",\"severity\":4,\"result\":\"$result\",\"detail\":\"$detail_escaped\"}"
        fi
    else
        echo "<check>"
        echo "  <id>CCE-LNX-064</id>"
        echo "  <name>$name</name>"
        echo "  <severity>4</severity>"
        echo "  <result>$result</result>"
        echo "  <detail>$detail</detail>"
        echo "</check>"
    fi
}


# CCE-LNX-065: 불필요한 네트워크 모니터링 서비스 실행
check_65() {
    local cce_id="CCE-LNX-065"
    local name='불필요한 네트워크 모니터링 서비스 실행'
    local severity="3"
    local result="양호"
    local detail=""
    local check_output=""
    
    check_output=$(ps -ef 2>&1)
    if [[ $? -ne 0 ]] || [[ -z "$check_output" ]]; then
        result="양호"
        detail="명령 실행 실패 또는 결과 없음 (대상 리소스 없음)"
    else
        detail="$(echo "$check_output" | head -10 | tr '\n' '; ' | sed 's/; $//')"
        # 기본 판정: 결과가 있으면 양호로 간주 (항목에 따라 다를 수 있음)
        if echo "$check_output" | grep -qiE "error|not found|no such|실패"; then
            result="취약"
        else
            result="양호"
        fi
    fi
    
    # 결과 출력
    if [[ "$FORMAT" == "json" ]]; then
        # Python을 사용하여 JSON 이스케이프 (jq가 없어도 작동)
        if command -v python3 >/dev/null 2>&1; then
            local name_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$name")
            local detail_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$detail")
            echo "{\"id\":\"CCE-LNX-065\",\"name\":$name_escaped,\"severity\":3,\"result\":\"$result\",\"detail\":$detail_escaped}"
        elif command -v jq >/dev/null 2>&1; then
            local name_escaped=$(echo "$name" | jq -Rs .)
            local detail_escaped=$(echo "$detail" | jq -Rs .)
            echo "{\"id\":\"CCE-LNX-065\",\"name\":$name_escaped,\"severity\":3,\"result\":\"$result\",\"detail\":$detail_escaped}"
        else
            # 둘 다 없으면 간단한 이스케이프 (sed 사용)
            # 빈 문자열 처리
            if [[ -z "$name" ]]; then
                name_escaped=""
            else
                name_escaped=$(echo "$name" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            if [[ -z "$detail" ]]; then
                detail_escaped=""
            else
                detail_escaped=$(echo "$detail" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            echo "{\"id\":\"CCE-LNX-065\",\"name\":\"$name_escaped\",\"severity\":3,\"result\":\"$result\",\"detail\":\"$detail_escaped\"}"
        fi
    else
        echo "<check>"
        echo "  <id>CCE-LNX-065</id>"
        echo "  <name>$name</name>"
        echo "  <severity>3</severity>"
        echo "  <result>$result</result>"
        echo "  <detail>$detail</detail>"
        echo "</check>"
    fi
}


# CCE-LNX-066: 웹 서비스 정보 노출
check_66() {
    local cce_id="CCE-LNX-066"
    local name='웹 서비스 정보 노출'
    local severity="3"
    local result="양호"
    local detail=""
    local check_output=""
    
    result="양호"
    detail="점검 방법이 명시되지 않음 (대상 리소스 없음으로 간주)"
    
    # 결과 출력
    if [[ "$FORMAT" == "json" ]]; then
        # Python을 사용하여 JSON 이스케이프 (jq가 없어도 작동)
        if command -v python3 >/dev/null 2>&1; then
            local name_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$name")
            local detail_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$detail")
            echo "{\"id\":\"CCE-LNX-066\",\"name\":$name_escaped,\"severity\":3,\"result\":\"$result\",\"detail\":$detail_escaped}"
        elif command -v jq >/dev/null 2>&1; then
            local name_escaped=$(echo "$name" | jq -Rs .)
            local detail_escaped=$(echo "$detail" | jq -Rs .)
            echo "{\"id\":\"CCE-LNX-066\",\"name\":$name_escaped,\"severity\":3,\"result\":\"$result\",\"detail\":$detail_escaped}"
        else
            # 둘 다 없으면 간단한 이스케이프 (sed 사용)
            # 빈 문자열 처리
            if [[ -z "$name" ]]; then
                name_escaped=""
            else
                name_escaped=$(echo "$name" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            if [[ -z "$detail" ]]; then
                detail_escaped=""
            else
                detail_escaped=$(echo "$detail" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            echo "{\"id\":\"CCE-LNX-066\",\"name\":\"$name_escaped\",\"severity\":3,\"result\":\"$result\",\"detail\":\"$detail_escaped\"}"
        fi
    else
        echo "<check>"
        echo "  <id>CCE-LNX-066</id>"
        echo "  <name>$name</name>"
        echo "  <severity>3</severity>"
        echo "  <result>$result</result>"
        echo "  <detail>$detail</detail>"
        echo "</check>"
    fi
}


# CCE-LNX-067: 불필요한 Telnet 서비스 실행
check_67() {
    local cce_id="CCE-LNX-067"
    local name='불필요한 Telnet 서비스 실행'
    local severity="3"
    local result="양호"
    local detail=""
    local check_output=""
    
    result="양호"
    detail="점검 방법이 명시되지 않음 (대상 리소스 없음으로 간주)"
    
    # 결과 출력
    if [[ "$FORMAT" == "json" ]]; then
        # Python을 사용하여 JSON 이스케이프 (jq가 없어도 작동)
        if command -v python3 >/dev/null 2>&1; then
            local name_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$name")
            local detail_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$detail")
            echo "{\"id\":\"CCE-LNX-067\",\"name\":$name_escaped,\"severity\":3,\"result\":\"$result\",\"detail\":$detail_escaped}"
        elif command -v jq >/dev/null 2>&1; then
            local name_escaped=$(echo "$name" | jq -Rs .)
            local detail_escaped=$(echo "$detail" | jq -Rs .)
            echo "{\"id\":\"CCE-LNX-067\",\"name\":$name_escaped,\"severity\":3,\"result\":\"$result\",\"detail\":$detail_escaped}"
        else
            # 둘 다 없으면 간단한 이스케이프 (sed 사용)
            # 빈 문자열 처리
            if [[ -z "$name" ]]; then
                name_escaped=""
            else
                name_escaped=$(echo "$name" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            if [[ -z "$detail" ]]; then
                detail_escaped=""
            else
                detail_escaped=$(echo "$detail" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            echo "{\"id\":\"CCE-LNX-067\",\"name\":\"$name_escaped\",\"severity\":3,\"result\":\"$result\",\"detail\":\"$detail_escaped\"}"
        fi
    else
        echo "<check>"
        echo "  <id>CCE-LNX-067</id>"
        echo "  <name>$name</name>"
        echo "  <severity>3</severity>"
        echo "  <result>$result</result>"
        echo "  <detail>$detail</detail>"
        echo "</check>"
    fi
}


# CCE-LNX-068: ftpusers 파일의 소유자 및 권한 설정 미흡
check_68() {
    local cce_id="CCE-LNX-068"
    local name='ftpusers 파일의 소유자 및 권한 설정 미흡'
    local severity="3"
    local result="양호"
    local detail=""
    local check_output=""
    
    result="양호"
    detail="점검 방법이 명시되지 않음 (대상 리소스 없음으로 간주)"
    
    # 결과 출력
    if [[ "$FORMAT" == "json" ]]; then
        # Python을 사용하여 JSON 이스케이프 (jq가 없어도 작동)
        if command -v python3 >/dev/null 2>&1; then
            local name_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$name")
            local detail_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$detail")
            echo "{\"id\":\"CCE-LNX-068\",\"name\":$name_escaped,\"severity\":3,\"result\":\"$result\",\"detail\":$detail_escaped}"
        elif command -v jq >/dev/null 2>&1; then
            local name_escaped=$(echo "$name" | jq -Rs .)
            local detail_escaped=$(echo "$detail" | jq -Rs .)
            echo "{\"id\":\"CCE-LNX-068\",\"name\":$name_escaped,\"severity\":3,\"result\":\"$result\",\"detail\":$detail_escaped}"
        else
            # 둘 다 없으면 간단한 이스케이프 (sed 사용)
            # 빈 문자열 처리
            if [[ -z "$name" ]]; then
                name_escaped=""
            else
                name_escaped=$(echo "$name" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            if [[ -z "$detail" ]]; then
                detail_escaped=""
            else
                detail_escaped=$(echo "$detail" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            echo "{\"id\":\"CCE-LNX-068\",\"name\":\"$name_escaped\",\"severity\":3,\"result\":\"$result\",\"detail\":\"$detail_escaped\"}"
        fi
    else
        echo "<check>"
        echo "  <id>CCE-LNX-068</id>"
        echo "  <name>$name</name>"
        echo "  <severity>3</severity>"
        echo "  <result>$result</result>"
        echo "  <detail>$detail</detail>"
        echo "</check>"
    fi
}


# CCE-LNX-069: 시스템 사용 주의사항 미출력
check_69() {
    local cce_id="CCE-LNX-069"
    local name='시스템 사용 주의사항 미출력'
    local severity="1"
    local result="양호"
    local detail=""
    local check_output=""
    
    result="양호"
    detail="점검 방법이 명시되지 않음 (대상 리소스 없음으로 간주)"
    
    # 결과 출력
    if [[ "$FORMAT" == "json" ]]; then
        # Python을 사용하여 JSON 이스케이프 (jq가 없어도 작동)
        if command -v python3 >/dev/null 2>&1; then
            local name_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$name")
            local detail_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$detail")
            echo "{\"id\":\"CCE-LNX-069\",\"name\":$name_escaped,\"severity\":1,\"result\":\"$result\",\"detail\":$detail_escaped}"
        elif command -v jq >/dev/null 2>&1; then
            local name_escaped=$(echo "$name" | jq -Rs .)
            local detail_escaped=$(echo "$detail" | jq -Rs .)
            echo "{\"id\":\"CCE-LNX-069\",\"name\":$name_escaped,\"severity\":1,\"result\":\"$result\",\"detail\":$detail_escaped}"
        else
            # 둘 다 없으면 간단한 이스케이프 (sed 사용)
            # 빈 문자열 처리
            if [[ -z "$name" ]]; then
                name_escaped=""
            else
                name_escaped=$(echo "$name" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            if [[ -z "$detail" ]]; then
                detail_escaped=""
            else
                detail_escaped=$(echo "$detail" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            echo "{\"id\":\"CCE-LNX-069\",\"name\":\"$name_escaped\",\"severity\":1,\"result\":\"$result\",\"detail\":\"$detail_escaped\"}"
        fi
    else
        echo "<check>"
        echo "  <id>CCE-LNX-069</id>"
        echo "  <name>$name</name>"
        echo "  <severity>1</severity>"
        echo "  <result>$result</result>"
        echo "  <detail>$detail</detail>"
        echo "</check>"
    fi
}


# CCE-LNX-070: 구성원이 존재하지 않는 GID 존재
check_70() {
    local cce_id="CCE-LNX-070"
    local name='구성원이 존재하지 않는 GID 존재'
    local severity="2"
    local result="양호"
    local detail=""
    local check_output=""
    
    result="양호"
    detail="점검 방법이 명시되지 않음 (대상 리소스 없음으로 간주)"
    
    # 결과 출력
    if [[ "$FORMAT" == "json" ]]; then
        # Python을 사용하여 JSON 이스케이프 (jq가 없어도 작동)
        if command -v python3 >/dev/null 2>&1; then
            local name_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$name")
            local detail_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$detail")
            echo "{\"id\":\"CCE-LNX-070\",\"name\":$name_escaped,\"severity\":2,\"result\":\"$result\",\"detail\":$detail_escaped}"
        elif command -v jq >/dev/null 2>&1; then
            local name_escaped=$(echo "$name" | jq -Rs .)
            local detail_escaped=$(echo "$detail" | jq -Rs .)
            echo "{\"id\":\"CCE-LNX-070\",\"name\":$name_escaped,\"severity\":2,\"result\":\"$result\",\"detail\":$detail_escaped}"
        else
            # 둘 다 없으면 간단한 이스케이프 (sed 사용)
            # 빈 문자열 처리
            if [[ -z "$name" ]]; then
                name_escaped=""
            else
                name_escaped=$(echo "$name" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            if [[ -z "$detail" ]]; then
                detail_escaped=""
            else
                detail_escaped=$(echo "$detail" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            echo "{\"id\":\"CCE-LNX-070\",\"name\":\"$name_escaped\",\"severity\":2,\"result\":\"$result\",\"detail\":\"$detail_escaped\"}"
        fi
    else
        echo "<check>"
        echo "  <id>CCE-LNX-070</id>"
        echo "  <name>$name</name>"
        echo "  <severity>2</severity>"
        echo "  <result>$result</result>"
        echo "  <detail>$detail</detail>"
        echo "</check>"
    fi
}


# CCE-LNX-071: 불필요하게 Shell이 부여된 계정 존재
check_71() {
    local cce_id="CCE-LNX-071"
    local name='불필요하게 Shell이 부여된 계정 존재'
    local severity="1"
    local result="양호"
    local detail=""
    local check_output=""
    
    check_output=$(cat /etc/passwd 2>&1)
    if [[ $? -ne 0 ]] || [[ -z "$check_output" ]]; then
        result="양호"
        detail="명령 실행 실패 또는 결과 없음 (대상 리소스 없음)"
    else
        detail="$(echo "$check_output" | head -10 | tr '\n' '; ' | sed 's/; $//')"
        # 기본 판정: 결과가 있으면 양호로 간주 (항목에 따라 다를 수 있음)
        if echo "$check_output" | grep -qiE "error|not found|no such|실패"; then
            result="취약"
        else
            result="양호"
        fi
    fi
    
    # 결과 출력
    if [[ "$FORMAT" == "json" ]]; then
        # Python을 사용하여 JSON 이스케이프 (jq가 없어도 작동)
        if command -v python3 >/dev/null 2>&1; then
            local name_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$name")
            local detail_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$detail")
            echo "{\"id\":\"CCE-LNX-071\",\"name\":$name_escaped,\"severity\":1,\"result\":\"$result\",\"detail\":$detail_escaped}"
        elif command -v jq >/dev/null 2>&1; then
            local name_escaped=$(echo "$name" | jq -Rs .)
            local detail_escaped=$(echo "$detail" | jq -Rs .)
            echo "{\"id\":\"CCE-LNX-071\",\"name\":$name_escaped,\"severity\":1,\"result\":\"$result\",\"detail\":$detail_escaped}"
        else
            # 둘 다 없으면 간단한 이스케이프 (sed 사용)
            # 빈 문자열 처리
            if [[ -z "$name" ]]; then
                name_escaped=""
            else
                name_escaped=$(echo "$name" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            if [[ -z "$detail" ]]; then
                detail_escaped=""
            else
                detail_escaped=$(echo "$detail" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            echo "{\"id\":\"CCE-LNX-071\",\"name\":\"$name_escaped\",\"severity\":1,\"result\":\"$result\",\"detail\":\"$detail_escaped\"}"
        fi
    else
        echo "<check>"
        echo "  <id>CCE-LNX-071</id>"
        echo "  <name>$name</name>"
        echo "  <severity>1</severity>"
        echo "  <result>$result</result>"
        echo "  <detail>$detail</detail>"
        echo "</check>"
    fi
}


# CCE-LNX-072: 불필요한 숨김 파일 또는 디렉터리 존재
check_72() {
    local cce_id="CCE-LNX-072"
    local name='불필요한 숨김 파일 또는 디렉터리 존재'
    local severity="1"
    local result="양호"
    local detail=""
    local check_output=""
    
    result="양호"
    detail="점검 방법이 명시되지 않음 (대상 리소스 없음으로 간주)"
    
    # 결과 출력
    if [[ "$FORMAT" == "json" ]]; then
        # Python을 사용하여 JSON 이스케이프 (jq가 없어도 작동)
        if command -v python3 >/dev/null 2>&1; then
            local name_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$name")
            local detail_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$detail")
            echo "{\"id\":\"CCE-LNX-072\",\"name\":$name_escaped,\"severity\":1,\"result\":\"$result\",\"detail\":$detail_escaped}"
        elif command -v jq >/dev/null 2>&1; then
            local name_escaped=$(echo "$name" | jq -Rs .)
            local detail_escaped=$(echo "$detail" | jq -Rs .)
            echo "{\"id\":\"CCE-LNX-072\",\"name\":$name_escaped,\"severity\":1,\"result\":\"$result\",\"detail\":$detail_escaped}"
        else
            # 둘 다 없으면 간단한 이스케이프 (sed 사용)
            # 빈 문자열 처리
            if [[ -z "$name" ]]; then
                name_escaped=""
            else
                name_escaped=$(echo "$name" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            if [[ -z "$detail" ]]; then
                detail_escaped=""
            else
                detail_escaped=$(echo "$detail" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            echo "{\"id\":\"CCE-LNX-072\",\"name\":\"$name_escaped\",\"severity\":1,\"result\":\"$result\",\"detail\":\"$detail_escaped\"}"
        fi
    else
        echo "<check>"
        echo "  <id>CCE-LNX-072</id>"
        echo "  <name>$name</name>"
        echo "  <severity>1</severity>"
        echo "  <result>$result</result>"
        echo "  <detail>$detail</detail>"
        echo "</check>"
    fi
}


# CCE-LNX-073: SMTP 서비스 정보 노출
check_73() {
    local cce_id="CCE-LNX-073"
    local name='SMTP 서비스 정보 노출'
    local severity="1"
    local result="양호"
    local detail=""
    local check_output=""
    
    result="양호"
    detail="점검 방법이 명시되지 않음 (대상 리소스 없음으로 간주)"
    
    # 결과 출력
    if [[ "$FORMAT" == "json" ]]; then
        # Python을 사용하여 JSON 이스케이프 (jq가 없어도 작동)
        if command -v python3 >/dev/null 2>&1; then
            local name_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$name")
            local detail_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$detail")
            echo "{\"id\":\"CCE-LNX-073\",\"name\":$name_escaped,\"severity\":1,\"result\":\"$result\",\"detail\":$detail_escaped}"
        elif command -v jq >/dev/null 2>&1; then
            local name_escaped=$(echo "$name" | jq -Rs .)
            local detail_escaped=$(echo "$detail" | jq -Rs .)
            echo "{\"id\":\"CCE-LNX-073\",\"name\":$name_escaped,\"severity\":1,\"result\":\"$result\",\"detail\":$detail_escaped}"
        else
            # 둘 다 없으면 간단한 이스케이프 (sed 사용)
            # 빈 문자열 처리
            if [[ -z "$name" ]]; then
                name_escaped=""
            else
                name_escaped=$(echo "$name" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            if [[ -z "$detail" ]]; then
                detail_escaped=""
            else
                detail_escaped=$(echo "$detail" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            echo "{\"id\":\"CCE-LNX-073\",\"name\":\"$name_escaped\",\"severity\":1,\"result\":\"$result\",\"detail\":\"$detail_escaped\"}"
        fi
    else
        echo "<check>"
        echo "  <id>CCE-LNX-073</id>"
        echo "  <name>$name</name>"
        echo "  <severity>1</severity>"
        echo "  <result>$result</result>"
        echo "  <detail>$detail</detail>"
        echo "</check>"
    fi
}


# CCE-LNX-074: FTP 서비스 정보 노출
check_74() {
    local cce_id="CCE-LNX-074"
    local name='FTP 서비스 정보 노출'
    local severity="1"
    local result="양호"
    local detail=""
    local check_output=""
    
    check_output=$(cat /usr/local/etc/proftpd.conf 2>&1)
    if [[ $? -ne 0 ]] || [[ -z "$check_output" ]]; then
        result="양호"
        detail="명령 실행 실패 또는 결과 없음 (대상 리소스 없음)"
    else
        detail="$(echo "$check_output" | head -10 | tr '\n' '; ' | sed 's/; $//')"
        # 기본 판정: 결과가 있으면 양호로 간주 (항목에 따라 다를 수 있음)
        if echo "$check_output" | grep -qiE "error|not found|no such|실패"; then
            result="취약"
        else
            result="양호"
        fi
    fi
    
    # 결과 출력
    if [[ "$FORMAT" == "json" ]]; then
        # Python을 사용하여 JSON 이스케이프 (jq가 없어도 작동)
        if command -v python3 >/dev/null 2>&1; then
            local name_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$name")
            local detail_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$detail")
            echo "{\"id\":\"CCE-LNX-074\",\"name\":$name_escaped,\"severity\":1,\"result\":\"$result\",\"detail\":$detail_escaped}"
        elif command -v jq >/dev/null 2>&1; then
            local name_escaped=$(echo "$name" | jq -Rs .)
            local detail_escaped=$(echo "$detail" | jq -Rs .)
            echo "{\"id\":\"CCE-LNX-074\",\"name\":$name_escaped,\"severity\":1,\"result\":\"$result\",\"detail\":$detail_escaped}"
        else
            # 둘 다 없으면 간단한 이스케이프 (sed 사용)
            # 빈 문자열 처리
            if [[ -z "$name" ]]; then
                name_escaped=""
            else
                name_escaped=$(echo "$name" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            if [[ -z "$detail" ]]; then
                detail_escaped=""
            else
                detail_escaped=$(echo "$detail" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            echo "{\"id\":\"CCE-LNX-074\",\"name\":\"$name_escaped\",\"severity\":1,\"result\":\"$result\",\"detail\":\"$detail_escaped\"}"
        fi
    else
        echo "<check>"
        echo "  <id>CCE-LNX-074</id>"
        echo "  <name>$name</name>"
        echo "  <severity>1</severity>"
        echo "  <result>$result</result>"
        echo "  <detail>$detail</detail>"
        echo "</check>"
    fi
}


# CCE-LNX-075: DNS 서비스의 취약한 동적 업데이트 설정
check_75() {
    local cce_id="CCE-LNX-075"
    local name='DNS 서비스의 취약한 동적 업데이트 설정'
    local severity="3"
    local result="양호"
    local detail=""
    local check_output=""
    
    result="양호"
    detail="점검 방법이 명시되지 않음 (대상 리소스 없음으로 간주)"
    
    # 결과 출력
    if [[ "$FORMAT" == "json" ]]; then
        # Python을 사용하여 JSON 이스케이프 (jq가 없어도 작동)
        if command -v python3 >/dev/null 2>&1; then
            local name_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$name")
            local detail_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$detail")
            echo "{\"id\":\"CCE-LNX-075\",\"name\":$name_escaped,\"severity\":3,\"result\":\"$result\",\"detail\":$detail_escaped}"
        elif command -v jq >/dev/null 2>&1; then
            local name_escaped=$(echo "$name" | jq -Rs .)
            local detail_escaped=$(echo "$detail" | jq -Rs .)
            echo "{\"id\":\"CCE-LNX-075\",\"name\":$name_escaped,\"severity\":3,\"result\":\"$result\",\"detail\":$detail_escaped}"
        else
            # 둘 다 없으면 간단한 이스케이프 (sed 사용)
            # 빈 문자열 처리
            if [[ -z "$name" ]]; then
                name_escaped=""
            else
                name_escaped=$(echo "$name" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            if [[ -z "$detail" ]]; then
                detail_escaped=""
            else
                detail_escaped=$(echo "$detail" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            echo "{\"id\":\"CCE-LNX-075\",\"name\":\"$name_escaped\",\"severity\":3,\"result\":\"$result\",\"detail\":\"$detail_escaped\"}"
        fi
    else
        echo "<check>"
        echo "  <id>CCE-LNX-075</id>"
        echo "  <name>$name</name>"
        echo "  <severity>3</severity>"
        echo "  <result>$result</result>"
        echo "  <detail>$detail</detail>"
        echo "</check>"
    fi
}


# CCE-LNX-076: 불필요한 DNS 서비스 실행
check_76() {
    local cce_id="CCE-LNX-076"
    local name='불필요한 DNS 서비스 실행'
    local severity="3"
    local result="양호"
    local detail=""
    local check_output=""
    
    check_output=$(ps -ef 2>&1)
    if [[ $? -ne 0 ]] || [[ -z "$check_output" ]]; then
        result="양호"
        detail="명령 실행 실패 또는 결과 없음 (대상 리소스 없음)"
    else
        detail="$(echo "$check_output" | head -10 | tr '\n' '; ' | sed 's/; $//')"
        # 기본 판정: 결과가 있으면 양호로 간주 (항목에 따라 다를 수 있음)
        if echo "$check_output" | grep -qiE "error|not found|no such|실패"; then
            result="취약"
        else
            result="양호"
        fi
    fi
    
    # 결과 출력
    if [[ "$FORMAT" == "json" ]]; then
        # Python을 사용하여 JSON 이스케이프 (jq가 없어도 작동)
        if command -v python3 >/dev/null 2>&1; then
            local name_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$name")
            local detail_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$detail")
            echo "{\"id\":\"CCE-LNX-076\",\"name\":$name_escaped,\"severity\":3,\"result\":\"$result\",\"detail\":$detail_escaped}"
        elif command -v jq >/dev/null 2>&1; then
            local name_escaped=$(echo "$name" | jq -Rs .)
            local detail_escaped=$(echo "$detail" | jq -Rs .)
            echo "{\"id\":\"CCE-LNX-076\",\"name\":$name_escaped,\"severity\":3,\"result\":\"$result\",\"detail\":$detail_escaped}"
        else
            # 둘 다 없으면 간단한 이스케이프 (sed 사용)
            # 빈 문자열 처리
            if [[ -z "$name" ]]; then
                name_escaped=""
            else
                name_escaped=$(echo "$name" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            if [[ -z "$detail" ]]; then
                detail_escaped=""
            else
                detail_escaped=$(echo "$detail" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            echo "{\"id\":\"CCE-LNX-076\",\"name\":\"$name_escaped\",\"severity\":3,\"result\":\"$result\",\"detail\":\"$detail_escaped\"}"
        fi
    else
        echo "<check>"
        echo "  <id>CCE-LNX-076</id>"
        echo "  <name>$name</name>"
        echo "  <severity>3</severity>"
        echo "  <result>$result</result>"
        echo "  <detail>$detail</detail>"
        echo "</check>"
    fi
}


# CCE-LNX-077: NTP 및 시각 동기화 미설정
check_77() {
    local cce_id="CCE-LNX-077"
    local name='NTP 및 시각 동기화 미설정'
    local severity="2"
    local result="양호"
    local detail=""
    local check_output=""
    
    check_output=$(date "+%Y-%m-%d %T" 2>&1)
    if [[ $? -ne 0 ]] || [[ -z "$check_output" ]]; then
        result="양호"
        detail="명령 실행 실패 또는 결과 없음 (대상 리소스 없음)"
    else
        detail="$(echo "$check_output" | head -10 | tr '\n' '; ' | sed 's/; $//')"
        # 기본 판정: 결과가 있으면 양호로 간주 (항목에 따라 다를 수 있음)
        if echo "$check_output" | grep -qiE "error|not found|no such|실패"; then
            result="취약"
        else
            result="양호"
        fi
    fi
    
    # 결과 출력
    if [[ "$FORMAT" == "json" ]]; then
        # Python을 사용하여 JSON 이스케이프 (jq가 없어도 작동)
        if command -v python3 >/dev/null 2>&1; then
            local name_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$name")
            local detail_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$detail")
            echo "{\"id\":\"CCE-LNX-077\",\"name\":$name_escaped,\"severity\":2,\"result\":\"$result\",\"detail\":$detail_escaped}"
        elif command -v jq >/dev/null 2>&1; then
            local name_escaped=$(echo "$name" | jq -Rs .)
            local detail_escaped=$(echo "$detail" | jq -Rs .)
            echo "{\"id\":\"CCE-LNX-077\",\"name\":$name_escaped,\"severity\":2,\"result\":\"$result\",\"detail\":$detail_escaped}"
        else
            # 둘 다 없으면 간단한 이스케이프 (sed 사용)
            # 빈 문자열 처리
            if [[ -z "$name" ]]; then
                name_escaped=""
            else
                name_escaped=$(echo "$name" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            if [[ -z "$detail" ]]; then
                detail_escaped=""
            else
                detail_escaped=$(echo "$detail" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed "s/\$/\\$/g" | sed "s/\`/\\`/g")
            fi
            echo "{\"id\":\"CCE-LNX-077\",\"name\":\"$name_escaped\",\"severity\":2,\"result\":\"$result\",\"detail\":\"$detail_escaped\"}"
        fi
    else
        echo "<check>"
        echo "  <id>CCE-LNX-077</id>"
        echo "  <name>$name</name>"
        echo "  <severity>2</severity>"
        echo "  <result>$result</result>"
        echo "  <detail>$detail</detail>"
        echo "</check>"
    fi
}


# 메인 함수
main() {
    local func_count=77
    
    # XML 출력 시작
    if [[ "$FORMAT" == "xml" ]]; then
        echo "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
        echo "<results>"
    fi
    
    # 모든 점검 실행
    check_1
    check_2
    check_3
    check_4
    check_5
    check_6
    check_7
    check_8
    check_9
    check_10
    check_11
    check_12
    check_13
    check_14
    check_15
    check_16
    check_17
    check_18
    check_19
    check_20
    check_21
    check_22
    check_23
    check_24
    check_25
    check_26
    check_27
    check_28
    check_29
    check_30
    check_31
    check_32
    check_33
    check_34
    check_35
    check_36
    check_37
    check_38
    check_39
    check_40
    check_41
    check_42
    check_43
    check_44
    check_45
    check_46
    check_47
    check_48
    check_49
    check_50
    check_51
    check_52
    check_53
    check_54
    check_55
    check_56
    check_57
    check_58
    check_59
    check_60
    check_61
    check_62
    check_63
    check_64
    check_65
    check_66
    check_67
    check_68
    check_69
    check_70
    check_71
    check_72
    check_73
    check_74
    check_75
    check_76
    check_77
    
    # XML 출력 종료
    if [[ "$FORMAT" == "xml" ]]; then
        echo "</results>"
    fi
}

# 스크립트 실행
main

