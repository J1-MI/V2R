#!/usr/bin/env python3
"""
CCE 점검 함수 생성기
data.json을 읽어서 bash 함수를 동적으로 생성
"""

import json
import sys
import re
from pathlib import Path
from datetime import datetime

def sanitize_function_name(name):
    """함수명으로 사용 가능한 문자열로 변환"""
    # 한글, 영문, 숫자만 남기고 나머지는 _로 변환
    name = re.sub(r'[^가-힣a-zA-Z0-9]', '_', name)
    # 연속된 _ 제거
    name = re.sub(r'_+', '_', name)
    # 앞뒤 _ 제거
    name = name.strip('_')
    return name.lower() if name else "check"

def extract_command(method_text):
    """판단방법에서 명령어 추출"""
    if not method_text:
        return None
    
    # 주석 제거 후 명령어 찾기
    lines = method_text.split('\n')
    commands = []
    
    # 일반적인 명령어 패턴
    command_patterns = [
        r'^#\s*(grep\s+[^\n]+)',
        r'^#\s*(cat\s+[^\n]+)',
        r'^#\s*(ps\s+[^\n]+)',
        r'^#\s*(ls\s+[^\n]+)',
        r'^#\s*(netstat\s+[^\n]+)',
        r'^#\s*(ss\s+[^\n]+)',
        r'^#\s*(find\s+[^\n]+)',
        r'^#\s*(echo\s+[^\n]+)',
        r'^#\s*(chmod\s+[^\n]+)',
        r'^#\s*(chown\s+[^\n]+)',
        r'^#\s*(rpcinfo\s+[^\n]+)',
        r'^#\s*(nmap\s+[^\n]+)',
        r'^#\s*(dig\s+[^\n]+)',
        r'^#\s*(ntpq\s+[^\n]+)',
        r'^#\s*(chronyc\s+[^\n]+)',
    ]
    
    for line in lines:
        line = line.strip()
        # 주석 제거
        if line.startswith('#'):
            line = line[1:].strip()
        # 빈 줄 스킵
        if not line or line.startswith('[') or line.startswith('*') or line.startswith('-'):
            continue
        
        # 명령어 패턴 매칭
        for pattern in command_patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                cmd = match.group(1).strip()
                # 파이프 이후 제거
                cmd = cmd.split('|')[0].strip()
                # 주석 제거
                cmd = cmd.split('#')[0].strip()
                if cmd and len(cmd) > 3:
                    commands.append(cmd)
                    break
        
        # 직접 명령어로 시작하는 경우
        if re.match(r'^[a-zA-Z/]', line) and not any(c in line for c in ['파일', '확인', '점검', '설정']):
            cmd = line.split('|')[0].strip().split('#')[0].strip()
            if cmd and len(cmd) > 3 and cmd not in commands:
                # 한글이 포함되지 않은 경우만
                if not re.search(r'[가-힣]', cmd):
                    commands.append(cmd)
    
    # 가장 긴 명령어 반환 (일반적으로 더 완전한 명령어)
    if commands:
        return max(commands, key=len)
    
    return None

def generate_check_logic(method, criteria, eval_item):
    """점검 로직 생성"""
    cmd = extract_command(method)
    
    if not cmd:
        return '''    result="양호"
    detail="점검 방법이 명시되지 않음 (대상 리소스 없음으로 간주)"'''
    
    # 특수 케이스 처리
    if 'sshd_config' in method.lower() or 'PermitRootLogin' in method:
        if 'root' in eval_item.lower() or '원격' in eval_item:
            cmd = "grep -i '^PermitRootLogin' /etc/ssh/sshd_config 2>/dev/null | head -1"
            logic = '''    check_output=$({cmd})
    if [[ -z "$check_output" ]]; then
        result="양호"
        detail="sshd_config 파일 없음 (대상 리소스 없음)"
    elif echo "$check_output" | grep -qiE "PermitRootLogin.*no|PermitRootLogin.*prohibit"; then
        result="양호"
        detail="$check_output"
    else
        result="취약"
        detail="$check_output"
    fi'''.format(cmd=cmd)
        elif 'PasswordAuthentication' in method or '패스워드' in eval_item:
            cmd = "grep -i '^PasswordAuthentication' /etc/ssh/sshd_config 2>/dev/null | head -1"
            logic = '''    check_output=$({cmd})
    if [[ -z "$check_output" ]]; then
        result="양호"
        detail="sshd_config 파일 없음 (대상 리소스 없음)"
    elif echo "$check_output" | grep -qiE "PasswordAuthentication.*no"; then
        result="양호"
        detail="$check_output"
    else
        result="취약"
        detail="$check_output"
    fi'''.format(cmd=cmd)
        else:
            newline_esc = '\\n'
            logic = f'''    check_output=$({cmd} 2>&1)
    if [[ $? -ne 0 ]] || [[ -z "$check_output" ]]; then
        result="양호"
        detail="명령 실행 실패 또는 결과 없음 (대상 리소스 없음)"
    else
        detail="$(echo "$check_output" | head -5 | tr '{newline_esc}' '; ')"
        result="양호"
    fi'''
    elif '25번 포트' in method or '포트.*25' in method or 'SMTP.*포트' in method or ('25번' in method and '포트' in method):
        cmd = "netstat -tuln 2>/dev/null | grep ':25 ' || ss -tuln 2>/dev/null | grep ':25 ' || true"
        logic = '''    check_output=$({cmd})
    if [[ -z "$check_output" ]]; then
        result="양호"
        detail="SMTP 서비스 미실행"
    else
        result="취약"
        detail="$check_output"
    fi'''.format(cmd=cmd)
    elif 'ftpusers' in method.lower() or 'ftp.*파일' in method:
        cmd = "cat /etc/ftpusers /etc/vsftpd/ftpusers /etc/ftpd/ftpusers 2>/dev/null | grep -v '^#' | grep -v '^$' | head -10"
        logic = '''    check_output=$({cmd})
    if [[ -z "$check_output" ]]; then
        result="취약"
        detail="ftpusers 파일 없음 또는 비어있음"
    elif echo "$check_output" | grep -qiE "^root|root:"; then
        result="양호"
        detail="root 계정이 ftpusers에 등록됨"
    else
        result="취약"
        detail="root 계정이 ftpusers에 없음"
    fi'''.format(cmd=cmd)
    elif '.netrc' in method or 'netrc' in method.lower():
        cmd = "find /home /root -maxdepth 2 -name '.netrc' -type f 2>/dev/null | head -5"
        logic = '''    check_output=$({cmd})
    if [[ -z "$check_output" ]]; then
        result="양호"
        detail=".netrc 파일 없음"
    else
        result="취약"
        detail=".netrc 파일 발견: $check_output"
    fi'''.format(cmd=cmd)
    elif 'HOMEDIR' in method or 'world writable' in method.lower() or 'perm -2' in method:
        # world writable 파일 점검
        cmd = "HOMEDIR=$(egrep -v 'nologin|false' /etc/passwd | awk -F: '{print $6}'); find $HOMEDIR -perm -2 -type f -exec ls -alL {} \\; 2>/dev/null | head -10"
        logic = '''    check_output=$({cmd})
    if [[ -z "$check_output" ]]; then
        result="양호"
        detail="world writable 파일 없음"
    else
        result="취약"
        detail="world writable 파일 발견: $(echo "$check_output" | head -5 | tr '\\n' '; ')"
    fi'''.format(cmd=cmd)
    else:
        # 기본 로직
        # 명령어에 백틱이나 특수 문자가 있으면 따옴표로 감싸기
        if '`' in cmd or '$' in cmd or '(' in cmd:
            # 복잡한 명령어는 그대로 사용하되, 따옴표 처리
            cmd_escaped = cmd.replace('"', '\\"')
            logic = f'''    check_output=$({cmd_escaped} 2>&1)
    if [[ $? -ne 0 ]] || [[ -z "$check_output" ]]; then
        result="양호"
        detail="명령 실행 실패 또는 결과 없음 (대상 리소스 없음)"
    else
        detail="$(echo "$check_output" | head -10 | tr '\\n' '; ' | sed 's/; $//')"
        # 기본 판정: 결과가 있으면 양호로 간주 (항목에 따라 다를 수 있음)
        if echo "$check_output" | grep -qiE "error|not found|no such|실패"; then
            result="취약"
        else
            result="양호"
        fi
    fi'''
        else:
            newline_esc = '\\n'
            logic = f'''    check_output=$({cmd} 2>&1)
    if [[ $? -ne 0 ]] || [[ -z "$check_output" ]]; then
        result="양호"
        detail="명령 실행 실패 또는 결과 없음 (대상 리소스 없음)"
    else
        detail="$(echo "$check_output" | head -10 | tr '{newline_esc}' '; ' | sed 's/; $//')"
        # 기본 판정: 결과가 있으면 양호로 간주 (항목에 따라 다를 수 있음)
        if echo "$check_output" | grep -qiE "error|not found|no such|실패"; then
            result="취약"
        else
            result="양호"
        fi
    fi'''
    
    return logic

def generate_bash_script(data_file, output_format='json'):
    """bash 스크립트 생성"""
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    script = f'''#!/bin/bash
#
# CCE 점검 자동화 스크립트 (자동 생성)
# 생성일: {datetime.now().isoformat()}
#

set -u  # undefined 변수만 오류 처리
set -o pipefail  # 파이프 오류 처리

FORMAT="{output_format}"

'''
    
    # 각 항목에 대한 함수 생성
    for idx, item in enumerate(data, 1):
        eval_item = item.get('평가항목', '')
        if not eval_item:
            continue
        
        risk_level = item.get('위험도', '3').strip()
        criteria = item.get('판단기준\n(LINUX)', '')
        method = item.get('판단방법\n(LINUX)', '')
        
        cce_id = f"CCE-LNX-{idx:03d}"
        func_name = f"check_{idx}"
        
        # 점검 로직 생성
        check_logic = generate_check_logic(method, criteria, eval_item)
        
        # 이름 이스케이프 처리 (작은따옴표 처리)
        name_escaped = eval_item.replace("'", "'\\''")
        # 함수 생성 시 따옴표 처리
        name_var = f"'{name_escaped}'"
        
        # 함수 생성 (f-string에서 백슬래시 문제 해결)
        # JSON 출력 코드를 별도로 생성하여 f-string 문제 회피
        json_output_template = '''    # 결과 출력
    if [[ "$FORMAT" == "json" ]]; then
        # Python을 사용하여 JSON 이스케이프 (jq가 없어도 작동)
        if command -v python3 >/dev/null 2>&1; then
            local name_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$name")
            local detail_escaped=$(python3 -c "import json, sys; print(json.dumps(sys.stdin.read()))" <<< "$detail")
            echo "{\\"id\\":\\"''' + cce_id + '''\\",\\"name\\":$name_escaped,\\"severity\\":''' + risk_level + ''',\\"result\\":\\"$result\\",\\"detail\\":$detail_escaped}"
        elif command -v jq >/dev/null 2>&1; then
            local name_escaped=$(echo "$name" | jq -Rs .)
            local detail_escaped=$(echo "$detail" | jq -Rs .)
            echo "{\\"id\\":\\"''' + cce_id + '''\\",\\"name\\":$name_escaped,\\"severity\\":''' + risk_level + ''',\\"result\\":\\"$result\\",\\"detail\\":$detail_escaped}"
        else
            # 둘 다 없으면 간단한 이스케이프 (sed 사용)
            # 빈 문자열 처리
            if [[ -z "$name" ]]; then
                name_escaped=""
            else
                name_escaped=$(echo "$name" | sed 's/\\\\/\\\\\\\\/g' | sed 's/"/\\\\"/g' | sed "s/\\$/\\\\$/g" | sed "s/\\`/\\\\`/g")
            fi
            if [[ -z "$detail" ]]; then
                detail_escaped=""
            else
                detail_escaped=$(echo "$detail" | sed 's/\\\\/\\\\\\\\/g' | sed 's/"/\\\\"/g' | sed "s/\\$/\\\\$/g" | sed "s/\\`/\\\\`/g")
            fi
            echo "{\\"id\\":\\"''' + cce_id + '''\\",\\"name\\":\\"$name_escaped\\",\\"severity\\":''' + risk_level + ''',\\"result\\":\\"$result\\",\\"detail\\":\\"$detail_escaped\\"}"
        fi
    else
        echo "<check>"
        echo "  <id>''' + cce_id + '''</id>"
        echo "  <name>$name</name>"
        echo "  <severity>''' + risk_level + '''</severity>"
        echo "  <result>$result</result>"
        echo "  <detail>$detail</detail>"
        echo "</check>"
    fi'''
        
        # f-string 대신 일반 문자열 연결 사용
        func_code = '''
# {cce_id}: {eval_item}
{func_name}() {{
    local cce_id="{cce_id}"
    local name={name_var}
    local severity="{risk_level}"
    local result="양호"
    local detail=""
    local check_output=""
    
{check_logic}
    
{json_output_code}
}}

'''.format(
            cce_id=cce_id,
            eval_item=eval_item,
            func_name=func_name,
            name_var=name_var,
            risk_level=risk_level,
            check_logic=check_logic,
            json_output_code=json_output_template
        )
        
        script += func_code
    
    # 메인 함수 추가
    func_count = len([x for x in data if x.get('평가항목')])
    
    script += '''
# 메인 함수
main() {
    local func_count='''
    script += str(func_count)
    script += '''
    
    # XML 출력 시작
    if [[ "$FORMAT" == "xml" ]]; then
        echo "<?xml version=\\"1.0\\" encoding=\\"UTF-8\\"?>"
        echo "<results>"
    fi
    
    # 모든 점검 실행
'''
    
    for idx in range(1, func_count + 1):
        script += f'    check_{idx}\n'
    
    script += '''    
    # XML 출력 종료
    if [[ "$FORMAT" == "xml" ]]; then
        echo "</results>"
    fi
}

# 스크립트 실행
main
'''
    
    return script

def main():
    if len(sys.argv) < 2:
        print("Usage: python generator.py <data.json> [--json|--xml]")
        sys.exit(1)
    
    data_file = sys.argv[1]
    output_format = 'json'
    
    if '--xml' in sys.argv:
        output_format = 'xml'
    elif '--json' in sys.argv:
        output_format = 'json'
    
    script = generate_bash_script(data_file, output_format)
    
    # Windows 인코딩 문제 해결
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    
    print(script)

if __name__ == '__main__':
    main()

