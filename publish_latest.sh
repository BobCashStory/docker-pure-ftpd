#!/usr/bin/env bash
docker build -t cashstory/pureftpd-api:latest . && \
docker push cashstory/pureftpd-api:latest && \
echo 'new image successfully published !'
