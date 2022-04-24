#!/bin/sh

set -ex

yarn --cwd frontend install
yarn --cwd frontend build
yarn --cwd tests install
docker-compose build projectx