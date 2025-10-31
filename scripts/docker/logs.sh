#!/bin/bash
# Docker 로그 보기 스크립트

SERVICE=${1:-}

if [ -z "$SERVICE" ]; then
    docker-compose logs -f
else
    docker-compose logs -f $SERVICE
fi

