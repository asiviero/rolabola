#!/usr/bin/env bash

apt-get update
apt-get install -y python3 python3-pip git firefox redis-server xvfb libjpeg-dev zlib1g-dev
wget https://github.com/mozilla/geckodriver/releases/download/v0.17.0/geckodriver-v0.17.0-linux64.tar.gz
tar -xvzf geckodriver*
chmod +x geckodriver
cp geckodriver /usr/local/bin/geckodriver
rm geckodriver*
