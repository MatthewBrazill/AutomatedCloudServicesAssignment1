#! /bin/sh

KEY_NAME=$1
INSTANCE_IP=$2
TEMP_FILE=$(mktemp)

cat $KEY_NAME.pem > $TEMP_FILE

$(scp -i $TEMP_FILE ../webserver_files/index.html ec2-user@$INSTANCE_IP:~/index.html)
$(scp -i $TEMP_FILE ./monitor.sh ec2-user@$INSTANCE_IP:~/monitor.sh)
$(ssh -i $TEMP_FILE ec2-user@$INSTANCE_IP 'mv ~/index.html /var/www/html/index.html')
$(ssh -i $TEMP_FILE ec2-user@$INSTANCE_IP '~/monitor.sh')

echo "success"