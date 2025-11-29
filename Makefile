# V2R 프로젝트 Makefile
# Docker 환경 관리 명령어

.PHONY: help build up down logs shell test init clean

help: ## 도움말 표시
	@echo "V2R Docker Commands:"
	@echo ""
	@echo "  make build       - Docker 이미지 빌드"
	@echo "  make up          - 모든 서비스 시작"
	@echo "  make down        - 모든 서비스 중지"
	@echo "  make logs        - 로그 보기"
	@echo "  make shell       - app 컨테이너에 접속"
	@echo "  make db-shell    - PostgreSQL에 접속"
	@echo "  make test        - 스캐너 테스트 실행"
	@echo "  make init        - 환경 초기화"
	@echo "  make clean       - 컨테이너 및 볼륨 정리"
	@echo "  make restart     - 서비스 재시작"
	@echo ""

build: ## Docker 이미지 빌드
	docker-compose build

up: ## 모든 서비스 시작
	docker-compose up -d
	@echo "Services started. Use 'make logs' to view logs."

down: ## 모든 서비스 중지
	docker-compose down

logs: ## 로그 보기
	docker-compose logs -f

shell: ## app 컨테이너에 접속
	docker-compose exec app /bin/bash

db-shell: ## PostgreSQL에 접속
	docker-compose exec postgres psql -U v2r -d v2r

test: ## 스캐너 테스트 실행
	docker-compose exec app python src/scanner/test_scanner.py

test-full: ## 전체 시스템 통합 테스트 실행
	docker-compose exec app python scripts/test/run_full_test.py

test-integration: ## 통합 테스트 실행
	docker-compose exec app python scripts/test/test_integration.py

test-pipeline: ## 파이프라인 테스트 실행
	docker-compose exec app python scripts/test/test_pipeline.py

init: ## 환경 초기화
	bash scripts/docker/init.sh

init-db: ## 데이터베이스 스키마 초기화
	docker-compose exec app python scripts/utils/init_db.py

clean: ## 컨테이너 및 볼륨 정리
	docker-compose down -v
	docker system prune -f

restart: ## 서비스 재시작
	docker-compose restart

rebuild: ## 이미지 재빌드 및 재시작
	docker-compose build --no-cache
	docker-compose up -d

status: ## 서비스 상태 확인
	docker-compose ps

