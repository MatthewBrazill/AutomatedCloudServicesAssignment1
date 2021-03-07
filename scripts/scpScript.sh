#! /bin/sh

KEY_NAME=../$1.pem
INSTANCE_IP=$2

$(chmod 600 $KEY_NAME)

$(echo $KEY_NAME)

# Setting up the index.html file
$(scp -o StrictHostKeyChecking=no -i $KEY_NAME ../webserver_files/index.html ec2-user@$INSTANCE_IP:~/index.html)
$(ssh -o StrictHostKeyChecking=no -i $KEY_NAME ec2-user@$INSTANCE_IP 'mv ~/index.html /var/www/html/index.html')

# Adding the monitoring script
$(scp -o StrictHostKeyChecking=no -i $KEY_NAME ./monitor.sh ec2-user@$INSTANCE_IP:~/monitor.sh)
$(ssh -o StrictHostKeyChecking=no -i $KEY_NAME ec2-user@$INSTANCE_IP '~/monitor.sh')