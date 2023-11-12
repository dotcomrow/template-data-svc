#!/bin/bash

docker build -t data-svc:latest .
docker run --rm -p 8080:8080 -e PORT=8080 -e PROJECT_ID=configuration-20231020 -e DATASET_NAME=configuration_dataset -v /Users/admin/secrets:/secrets -e GOOGLE_APPLICATION_CREDENTIALS=/secrets/google.key  data-svc:latest
