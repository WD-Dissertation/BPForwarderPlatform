#!/bin/bash


apt-get update

apt-get install python3-pip python3-dev build-essential libssl-dev libffi-dev python3-setuptools nginx

#Certbot for generating HTTPS certificate and installing
snap install core
snap refresh core
apt-get remove certbot
snap install --classic certbot
ln -s /snap/bin/certbot /usr/bin/certbot

pip3 install virtualenv

echo "All packages installed"

virtualenv BPForwarderEnv

source BPForwarderEnv/bin/activate

echo "Virtual Environment activated"

/home/ubuntu/BPForwarder/BPForwarderEnv/bin/pip install wheel

/home/ubuntu/BPForwarder/BPForwarderEnv/bin/pip install gunicorn flask

cp /home/ubuntu/BPForwarder/BPForwarderPlatform-0.14/app.py .

cp /home/ubuntu/BPForwarder/BPForwarderPlatform-0.14/wsgi.py .

cp /home/ubuntu/BPForwarder/BPForwarderPlatform-0.14/BPFconf.JSON .

deactivate
echo "Virtual Environment deactivated"

#Copy .service file to /etc/systemd/system/
cp /home/ubuntu/BPForwarder/BPForwarderPlatform-0.14/BPForwarder.service /etc/systemd/system/

systemctl start BPForwarder

systemctl enable BPForwarder

#systemctl status BPForwarder

echo "Flask and Gunicorn configured"

cp /home/ubuntu/BPForwarder/BPForwarderPlatform-0.14/BPForwarderNGINXserverblockconfigHTTP /etc/nginx/sites-available/

ln -s /etc/nginx/sites-available/BPForwarderNGINXserverblockconfigHTTP /etc/nginx/sites-enabled

rm /etc/nginx/sites-enabled/default

nginx -t

gpasswd -a www-data ubuntu

systemctl restart nginx
#nginx -s reload

certbot --nginx

ufw allow 'Nginx Full'

echo "Nginx webserver configured"

echo "BPForwarder is now Live!"

echo -e "\nProtocol 2" >> /etc/ssh/sshd_config
systemctl reload sshd
