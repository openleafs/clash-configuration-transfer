#!/bin/bash
sudo docker stop clash
echo "stop container clash"

sudo docker rm clash
echo "rm container clash"

sudo docker image rm clash/config-transfer
echo "rm image clash/config-transfer"

sudo docker build -t clash/config-transfer .
echo "build a new image: clash/config-transfer"

sudo docker volume rm clash_resource
echo "rm a volume: clash_resource"

sudo docker volume create clash_resource
echo "create a volume: clash_resource"

sudo docker run -d -p 5000:5000 --name clash --restart unless-stopped -v clash_resource:/app/resource clash/config-transfer
echo "run a new container: clash"
