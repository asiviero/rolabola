#!/usr/bin/env bash

apt-get update
apt-get install -y python3 python3-pip git firefox
pip3 install django==1.8
pip3 install --upgrade selenium
pip3 install factory_boy
pip3 install fake-factory
pip3 install Pillow
pip3 install django-material
pip3 install python-dateutil
