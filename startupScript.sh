#! /bin/sh

sudo yum update
sudo yum install httpd -y
sudo systemctl enable httpd
sudo systemctl start httpd