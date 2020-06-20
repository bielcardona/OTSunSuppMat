#!/usr/bin/env bash

add-apt-repository -y ppa:freecad-maintainers/freecad-stable
apt-get update
apt-get install -y libfreecad-python3-0.18
DEBIAN_FRONTEND=noninteractive apt-get install -y python3-pip
pip3 install pytest
mkdir -p /home/vagrant/.local/lib/python3.6/site-packages
echo "/usr/lib/freecad-python3/lib" > /home/vagrant/.local/lib/python3.6/site-packages/freecad.pth
pip3 install otsun
