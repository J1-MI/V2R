#!/bin/bash
set -e

# 로그 설정
exec > >(tee /var/log/user-data.log|logger -t user-data -s 2>/dev/console) 2>&1
echo "Starting user-data script for web server - $(date)"

# 패키지 업데이트
export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get upgrade -y

# 기본 패키지 설치
apt-get install -y \
    curl \
    wget \
    git \
    unzip \
    docker.io \
    docker-compose \
    apache2 \
    mysql-server \
    php \
    php-mysql \
    php-cli \
    libapache2-mod-php \
    python3 \
    python3-pip

# Docker 서비스 시작
systemctl enable docker
systemctl start docker

# MySQL 기본 설정 (의도적 취약 설정)
mysql -e "CREATE DATABASE IF NOT EXISTS dvwa;"
mysql -e "CREATE DATABASE IF NOT EXISTS testdb;"
mysql -e "CREATE USER IF NOT EXISTS 'dvwa'@'%' IDENTIFIED BY 'p@ssw0rd';"
mysql -e "GRANT ALL PRIVILEGES ON dvwa.* TO 'dvwa'@'%';"
mysql -e "GRANT ALL PRIVILEGES ON testdb.* TO 'dvwa'@'%';"
mysql -e "FLUSH PRIVILEGES;"

# MySQL 외부 접근 허용 (의도적 취약 설정)
sed -i 's/bind-address.*/bind-address = 0.0.0.0/' /etc/mysql/mysql.conf.d/mysqld.cnf || \
sed -i 's/bind-address.*/bind-address = 0.0.0.0/' /etc/mysql/my.cnf
systemctl restart mysql

# Apache 설정
systemctl enable apache2
systemctl start apache2

# DVWA 배포 디렉토리 생성
mkdir -p /var/www/html/dvwa
cd /var/www/html/dvwa

# DVWA 다운로드 (간단한 취약 웹앱 예시)
if [ ! -f "index.php" ]; then
    # 기본 취약 PHP 페이지 생성
    cat > index.php << 'EOF'
<?php
// 의도적 취약 웹페이지 예시
error_reporting(E_ALL);
ini_set('display_errors', 1);

if (isset($_GET['cmd'])) {
    echo "<pre>";
    system($_GET['cmd']);  // Command Injection 취약점
    echo "</pre>";
}

if (isset($_POST['username']) && isset($_POST['password'])) {
    // SQL Injection 취약점 예시
    $conn = mysqli_connect('localhost', 'dvwa', 'p@ssw0rd', 'dvwa');
    $query = "SELECT * FROM users WHERE username='" . $_POST['username'] . "' AND password='" . $_POST['password'] . "'";
    $result = mysqli_query($conn, $query);
    if ($result && mysqli_num_rows($result) > 0) {
        echo "Login successful (vulnerable to SQL injection)";
    } else {
        echo "Login failed";
    }
}
?>
<!DOCTYPE html>
<html>
<head><title>Vulnerable Test App</title></head>
<body>
<h1>Vulnerability Test Application</h1>
<p><strong>Warning:</strong> This application contains intentional vulnerabilities for testing purposes only.</p>
<h2>Command Injection Test</h2>
<form method="GET">
    <input type="text" name="cmd" placeholder="Enter command" value="<?php echo isset($_GET['cmd']) ? htmlspecialchars($_GET['cmd']) : ''; ?>">
    <button type="submit">Execute</button>
</form>
<h2>SQL Injection Test</h2>
<form method="POST">
    <input type="text" name="username" placeholder="Username">
    <input type="password" name="password" placeholder="Password">
    <button type="submit">Login</button>
</form>
</body>
</html>
EOF
    chown www-data:www-data /var/www/html/dvwa -R
fi

# Juice Shop 배포 (Docker)
mkdir -p /opt/juice-shop
cd /opt/juice-shop
docker pull bkimminich/juice-shop
cat > docker-compose.yml << 'EOF'
version: '3'
services:
  juice-shop:
    image: bkimminich/juice-shop
    ports:
      - "3000:3000"
    restart: unless-stopped
EOF
docker-compose up -d

# SSH 취약 설정 (의도적 취약 설정)
echo "Configuring SSH for vulnerability testing..."
sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config
sed -i 's/PasswordAuthentication no/PasswordAuthentication yes/' /etc/ssh/sshd_config
sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config
sed -i 's/PermitRootLogin no/PermitRootLogin yes/' /etc/ssh/sshd_config
# root 비밀번호 설정 (테스트용 - 실제 환경에서는 절대 사용 금지)
echo "root:v2r_test_password" | chpasswd
systemctl restart sshd
echo "SSH vulnerable configuration applied"

# Text4shell 취약 웹앱 배포 (Spring Boot 버전 사용)
echo "Deploying Text4shell vulnerable application..."
apt-get install -y openjdk-17-jdk maven
mkdir -p /opt/text4shell-app
cd /opt/text4shell-app

# text4shell_app.sh 스크립트 복사 및 실행
cat > text4shell_app.sh << 'TEXT4SHELL_EOF'
#!/bin/bash
# Text4shell (CVE-2022-42889) 취약 웹 애플리케이션 배포 스크립트
set -e

exec > >(tee /var/log/text4shell-setup.log|logger -t text4shell -s 2>/dev/console) 2>&1
echo "Starting Text4shell vulnerable app setup - $(date)"

# Java 및 Maven 설치
export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y openjdk-17-jdk maven git curl

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

# systemd 서비스 등록
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

echo "Text4shell vulnerable app setup completed - $(date)"
echo "Application URL: http://$(curl -s ifconfig.me):8080/api/test"
TEXT4SHELL_EOF

chmod +x text4shell_app.sh
bash text4shell_app.sh
    
    # 간단한 취약 Java 앱 (Spring Boot 없이)
    cat > Text4ShellTest.java << 'JAVAEOF'
import org.apache.commons.text.StringSubstitutor;
import java.io.*;
import java.net.*;
import java.util.*;

public class Text4ShellTest {
    public static void main(String[] args) throws Exception {
        ServerSocket server = new ServerSocket(8080);
        System.out.println("Text4shell vulnerable server started on port 8080");
        
        while (true) {
            Socket client = server.accept();
            new Thread(() -> {
                try {
                    BufferedReader in = new BufferedReader(new InputStreamReader(client.getInputStream()));
                    PrintWriter out = new PrintWriter(client.getOutputStream(), true);
                    
                    String request = in.readLine();
                    if (request != null && request.contains("GET")) {
                        String response = "HTTP/1.1 200 OK\r\n\r\n";
                        response += "<html><body>";
                        response += "<h1>Text4shell Test</h1>";
                        response += "<p>Use: ?input=${script:javascript:java.lang.Runtime.getRuntime().exec('id')}</p>";
                        
                        // 쿼리 파라미터 추출
                        if (request.contains("input=")) {
                            String input = request.substring(request.indexOf("input=") + 6);
                            input = input.split(" ")[0];
                            input = URLDecoder.decode(input, "UTF-8");
                            
                            // 취약한 문자열 보간
                            StringSubstitutor sub = new StringSubstitutor();
                            String result = sub.replace(input);
                            response += "<p>Result: " + result + "</p>";
                        }
                        
                        response += "</body></html>";
                        out.println(response);
                    }
                    client.close();
                } catch (Exception e) {
                    e.printStackTrace();
                }
            }).start();
        }
    }
}
JAVAEOF
    
    # Maven 프로젝트 생성
    mkdir -p src/main/java
    mv Text4ShellTest.java src/main/java/
    
    cat > pom.xml << 'EOF'
<?xml version="1.0"?>
<project>
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.v2r</groupId>
    <artifactId>text4shell</artifactId>
    <version>1.0</version>
    <dependencies>
        <dependency>
            <groupId>org.apache.commons</groupId>
            <artifactId>commons-text</artifactId>
            <version>1.9</version>
        </dependency>
    </dependencies>
    <build>
        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-compiler-plugin</artifactId>
                <version>3.8.1</version>
                <configuration>
                    <source>17</source>
                    <target>17</target>
                </configuration>
            </plugin>
        </plugins>
    </build>
</project>
EOF
    
    mvn compile exec:java -Dexec.mainClass="Text4ShellTest" > /var/log/text4shell.log 2>&1 &
    echo "Text4shell app started on port 8080"
fi

# Apache VirtualHost 설정
cat > /etc/apache2/sites-available/dvwa.conf << 'EOF'
<VirtualHost *:80>
    ServerName localhost
    DocumentRoot /var/www/html/dvwa
    <Directory /var/www/html/dvwa>
        Options Indexes FollowSymLinks
        AllowOverride All
        Require all granted
    </Directory>
</VirtualHost>
EOF
a2ensite dvwa.conf
a2enmod rewrite
systemctl restart apache2

# 로그 파일 생성
touch /var/log/v2r-web-server.log
chmod 666 /var/log/v2r-web-server.log

echo "Web server setup completed - $(date)"
echo "DVWA: http://$(curl -s ifconfig.me)/dvwa"
echo "Juice Shop: http://$(curl -s ifconfig.me):3000"

