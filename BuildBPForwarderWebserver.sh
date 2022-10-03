#!/bin/bash


apt-get update

apt-get install python3-pip python3-dev build-essential libssl-dev libffi-dev python3-setuptools nginx

pip3 install virtualenv

virtualenv BPForwarderEnv

sudo -u ubuntu source BPForwarderEnv/bin/activate

/home/ubuntu/BPForwarder/BPForwarderEnv/bin/pip install wheel

/home/ubuntu/BPForwarder/BPForwarderEnv/bin/pip install gunicorn flask

cp /home/ubuntu/BPForwarder/BPForwarderPlatform-0.3/app.py .

cp /home/ubuntu/BPForwarder/BPForwarderPlatform-0.3/wsgi.py .

cp /home/ubuntu/BPForwarder/BPForwarderPlatform-0.3/BPFconf.JSON .

sudo -u ubuntu deactivate

#Copy .service file to /etc/systemd/system/
cp /home/ubuntu/BPForwarder/BPForwarderPlatform-0.3/BPForwarder.service /etc/systemd/system/

systemctl start BPForwarder

systemctl enable BPForwarder

systemctl status BPForwarder

cp /home/ubuntu/BPForwarder/BPForwarderPlatform-0.3/BPForwarderNGINXserverblockconfigHTTP /etc/nginx/sites-available/

ln -s /etc/nginx/sites-available/BPForwarderNGINXserverblockconfigHTTP /etc/nginx/sites-enabled

rm /etc/nginx/sites-enabled/default

nginx -t

systemctl restart nginx

ufw allow 'Nginx Full'

echo "BPForwarder is now Live!"