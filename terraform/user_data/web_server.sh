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

