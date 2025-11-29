"""
데이터베이스 연결 관리 모듈
PostgreSQL 연결 및 기본 작업을 처리합니다.
"""

import logging
from typing import Optional, Dict, Any
from sqlalchemy import create_engine, Engine, text, inspect
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
from contextlib import contextmanager

from src.config import (
    DB_HOST,
    DB_PORT,
    DB_NAME,
    DB_USER,
    DB_PASSWORD
)

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """데이터베이스 연결 관리 클래스"""

    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[str] = None,
        database: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None
    ):
        """
        Args:
            host: DB 호스트 (기본값: config에서 읽음)
            port: DB 포트 (기본값: config에서 읽음)
            database: DB 이름 (기본값: config에서 읽음)
            user: DB 사용자 (기본값: config에서 읽음)
            password: DB 비밀번호 (기본값: config에서 읽음)
        """
        self.host = host or DB_HOST
        self.port = port or DB_PORT
        self.database = database or DB_NAME
        self.user = user or DB_USER
        self.password = password or DB_PASSWORD

        self.engine: Optional[Engine] = None
        self.SessionLocal: Optional[sessionmaker] = None

    def get_connection_string(self) -> str:
        """데이터베이스 연결 문자열 생성"""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"

    def connect(self) -> Engine:
        """
        데이터베이스 연결 생성

        Returns:
            SQLAlchemy Engine 객체
        """
        try:
            connection_string = self.get_connection_string()
            
            self.engine = create_engine(
                connection_string,
                poolclass=NullPool,  # 연결 풀 사용 안 함
                echo=False,  # SQL 쿼리 로그 비활성화
                connect_args={
                    "connect_timeout": 10,
                    "application_name": "v2r"
                }
            )

            # 연결 테스트
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))

            self.SessionLocal = sessionmaker(
                bind=self.engine,
                autocommit=False,
                autoflush=False
            )

            logger.info(f"Database connected: {self.host}:{self.port}/{self.database}")
            return self.engine

        except Exception as e:
            logger.error(f"Database connection failed: {str(e)}")
            raise

    @contextmanager
    def get_session(self):
        """
        데이터베이스 세션 컨텍스트 매니저

        Usage:
            with db.get_session() as session:
                # DB 작업 수행
        """
        if self.engine is None:
            self.connect()

        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def test_connection(self) -> bool:
        """
        데이터베이스 연결 테스트

        Returns:
            연결 성공 여부
        """
        try:
            if self.engine is None:
                self.connect()
            
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT version()"))
                version = result.fetchone()[0]
                logger.info(f"PostgreSQL version: {version}")
                return True

        except Exception as e:
            logger.error(f"Connection test failed: {str(e)}")
            return False

    def execute_sql_file(self, filepath: str) -> bool:
        """
        SQL 파일 실행 (스키마 생성 등)

        Args:
            filepath: SQL 파일 경로

        Returns:
            실행 성공 여부
        """
        try:
            if self.engine is None:
                self.connect()

            with open(filepath, 'r', encoding='utf-8') as f:
                sql_content = f.read()

            # SQL 문을 세미콜론으로 분리
            statements = [s.strip() for s in sql_content.split(';') if s.strip()]

            with self.engine.connect() as conn:
                for statement in statements:
                    if statement:
                        conn.execute(text(statement))
                conn.commit()

            logger.info(f"SQL file executed: {filepath}")
            return True

        except Exception as e:
            logger.error(f"SQL file execution failed: {filepath} - {str(e)}")
            return False

    def close(self):
        """데이터베이스 연결 종료"""
        if self.engine:
            self.engine.dispose()
            logger.info("Database connection closed")


# 전역 데이터베이스 인스턴스
_db_instance: Optional[DatabaseConnection] = None


def get_db() -> DatabaseConnection:
    """전역 데이터베이스 인스턴스 가져오기 (싱글톤)"""
    global _db_instance
    if _db_instance is None:
        _db_instance = DatabaseConnection()
        _db_instance.connect()
    return _db_instance


def initialize_database(schema_file: Optional[str] = None) -> bool:
    """
    데이터베이스 초기화 (스키마 생성)

    Args:
        schema_file: 스키마 파일 경로 (None이면 기본 경로 사용)

    Returns:
        초기화 성공 여부
    """
    from pathlib import Path
    
    if schema_file is None:
        schema_file = Path(__file__).parent / "schema.sql"

    db = get_db()

    if not db.test_connection():
        logger.error("Database connection failed, cannot initialize")
        return False

    # 이미 스키마가 생성되어 있으면 schema.sql 재실행을 생략
    try:
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        if "scan_results" in tables and "poc_reproductions" in tables:
            logger.info("Database schema already initialized, skipping schema.sql execution")
            return True
    except Exception as e:
        # 스키마 상태를 확인하지 못한 경우에만 기존 방식대로 진행
        logger.warning(f"Failed to inspect existing schema (will try to run schema.sql): {e}")

    return db.execute_sql_file(str(schema_file))

