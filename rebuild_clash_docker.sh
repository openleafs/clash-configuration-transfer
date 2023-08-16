# !/bin/bash
sudo docker stop clash
echo "stop container clash"

sudo docker rm clash
echo "rm container clash"

sudo docker image rm clash/config-transfer
echo "rm image clash/config-transfer"

sudo docker build -t clash/config-transfer .
echo "build a new image: clash/config-transfer"

sudo docker volume create allowed-ips
echo "create a volume: allowed-ips"

sudo docker run -d -p 5000:5000 --name clash -v allowed-ips:/app/template clash/config-transfer
echo "run a new container: clash"
