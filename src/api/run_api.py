"""
Flask API 서버 실행 진입점
"""

import os
import logging
from src.api.app import create_app

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """API 서버 실행"""
    # 설정 모드 결정
    config_name = os.getenv("FLASK_ENV", "development")
    
    # Flask 앱 생성
    app = create_app(config_name)
    
    # 서버 실행
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "5000"))
    debug = config_name == "development"
    
    logger.info(f"Flask API 서버 시작: http://{host}:{port}")
    logger.info(f"모드: {config_name}, 디버그: {debug}")
    
    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    main()

