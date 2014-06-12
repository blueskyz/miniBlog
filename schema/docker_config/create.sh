#!/usr/bin/env bash

docker.io run -d -m 3G -h 'hopez' -p 80:80 -p 36000:22 -p 37000:37000 -p 37064:37064 -v /data:/data -w /data --name ucare_hopez ubuntu_hopez /data/docker_config/hopez
docker.io run -d -m 512M -p 35022:22 -v /data:/data -w /data --name ucare_scrapy -h 'hopez_scrapy' ubuntu_scrapy /data/docker_config/scrapy
