#!/bin/bash

if [ -z "$1" ]; then
  echo "Usage: $0 <version>"
  exit 1
fi

VERSION="1.0.$1"
IMAGE="sre-playground-worker"
DOCKER_USER="tsandas"

echo "Building image ${IMAGE}:${VERSION}"
docker build -t ${IMAGE}:${VERSION} .

echo "Tagging image ${DOCKER_USER}/${IMAGE}:${VERSION}"
docker tag ${IMAGE}:${VERSION} ${DOCKER_USER}/${IMAGE}:${VERSION}

echo "Pushing image ${DOCKER_USER}/${IMAGE}:${VERSION}"
docker push ${DOCKER_USER}/${IMAGE}:${VERSION}

echo "Done."