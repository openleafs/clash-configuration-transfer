#!/bin/bash
sudo curl http://127.0.0.1:5000/allow
echo "refresh allow list"

sudo systemctl restart nginx
echo "restart nginx"