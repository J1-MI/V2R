# 웹 서버 EC2 인스턴스 (취약 앱 배포용)
resource "aws_instance" "web_server" {
  ami                    = var.instance_ami != "" ? var.instance_ami : data.aws_ami.ubuntu.id
  instance_type          = var.instance_type
  key_name              = length(aws_key_pair.main) > 0 ? aws_key_pair.main[0].key_name : null
  vpc_security_group_ids = [aws_security_group.web_server.id]
  subnet_id              = aws_subnet.public[0].id

  root_block_device {
    volume_type = "gp3"
    volume_size = 20
    encrypted   = true
  }

  user_data = base64encode(file("${path.module}/user_data/web_server.sh"))

  tags = merge(
    var.tags,
    {
      Name        = "${var.project_name}-${var.environment}-web-server"
      Role        = "vulnerable-web-app"
      Warning     = "Contains-Intentionally-Vulnerable-Config"
    }
  )
}

# 스캐너/컨트롤러 EC2 인스턴스
resource "aws_instance" "scanner" {
  ami                    = var.instance_ami != "" ? var.instance_ami : data.aws_ami.ubuntu.id
  instance_type          = "t3.small"  # 스캐너는 작은 인스턴스로 충분
  key_name              = length(aws_key_pair.main) > 0 ? aws_key_pair.main[0].key_name : null
  vpc_security_group_ids = [aws_security_group.scanner.id]
  subnet_id              = aws_subnet.public[0].id

  root_block_device {
    volume_type = "gp3"
    volume_size = 20
    encrypted   = true
  }

  user_data = base64encode(file("${path.module}/user_data/scanner.sh"))

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-${var.environment}-scanner"
      Role = "scanner-controller"
    }
  )
}

# Ubuntu 22.04 LTS AMI 조회
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/*/ubuntu-jammy-22.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }

  filter {
    name   = "architecture"
    values = ["x86_64"]
  }
}

# SSH 키 페어 (선택적 - keys/id_rsa.pub 파일이 있는 경우만)
# 키가 없으면 EC2 인스턴스는 키 없이 생성됩니다
# 생성 방법: mkdir -p keys && ssh-keygen -t rsa -b 4096 -f keys/id_rsa -N ""
resource "aws_key_pair" "main" {
  count      = local.has_ssh_key ? 1 : 0
  key_name   = "${var.project_name}-${var.environment}-key"
  public_key = local.ssh_public_key
  
  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-${var.environment}-key"
    }
  )
}
