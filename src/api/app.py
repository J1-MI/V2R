"""
Flask 애플리케이션 팩토리
Flask 앱 생성 및 Blueprint 등록
"""

from flask import Flask
from src.config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
import logging

logger = logging.getLogger(__name__)


def create_app(config_name: str = "development") -> Flask:
    """
    Flask 애플리케이션 팩토리 함수
    
    Args:
        config_name: 설정 이름 (development, production)
    
    Returns:
        Flask 애플리케이션 인스턴스
    """
    app = Flask(__name__)
    
    # 기본 설정
    app.config["SECRET_KEY"] = "v2r-agent-api-secret-key"  # 프로덕션에서는 환경 변수로 변경
    app.config["JSON_AS_ASCII"] = False
    app.config["JSONIFY_PRETTYPRINT_REGULAR"] = True
    
    # 데이터베이스 설정 (참고용, 실제 연결은 repository에서 처리)
    app.config["DATABASE"] = {
        "host": DB_HOST,
        "port": DB_PORT,
        "database": DB_NAME,
        "user": DB_USER,
        "password": DB_PASSWORD
    }
    
    # Blueprint 등록
    from src.api.blueprints.agents import agents_bp
    app.register_blueprint(agents_bp, url_prefix="/api")
    
    logger.info("Flask 애플리케이션 초기화 완료")
    
    return app

