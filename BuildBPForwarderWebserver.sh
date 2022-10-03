#!/bin/bash


sudo apt-get update

sudo apt-get install python3-pip python3-dev build-essential libssl-dev libffi-dev python3-setuptools nginx

sudo pip3 install virtualenv

sudo virtualenv BPForwarderEnv

source BPForwarderEnv/bin/activate

sudo /home/ubuntu/BPForwarder/BPForwarderEnv/bin/pip install wheel

sudo /home/ubuntu/BPForwarder/BPForwarderEnv/bin/pip install gunicorn flask

sudo cp /home/ubuntu/BPForwarder/BPForwarderPlatform-0.3/app.py .

sudo cp /home/ubuntu/BPForwarder/BPForwarderPlatform-0.3/wsgi.py .

sudo cp /home/ubuntu/BPForwarder/BPForwarderPlatform-0.3/BPFconf.JSON .

deactivate

#Copy .service file to /etc/systemd/system/
sudo cp /home/ubuntu/BPForwarder/BPForwarderPlatform-0.3/BPForwarder.service /etc/systemd/system/

sudo systemctl start BPForwarder

sudo systemctl enable BPForwarder

sudo systemctl status BPForwarder

sudo cp /home/ubuntu/BPForwarder/BPForwarderPlatform-0.3/BPForwarderNGINXserverblockconfigHTTP /etc/nginx/sites-available/

sudo ln -s /etc/nginx/sites-available/BPForwarderNGINXserverblockconfigHTTP /etc/nginx/sites-enabled

sudo rm /etc/nginx/sites-enabled/default

sudo nginx -t

sudo systemctl restart nginx

sudo ufw allow 'Nginx Full'

echo "BPForwarder is now Live!"