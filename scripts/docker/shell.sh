#!/bin/bash
# Docker 컨테이너에 접속하는 스크립트

CONTAINER=${1:-app}

echo "Connecting to container: $CONTAINER"
docker-compose exec $CONTAINER /bin/bash

