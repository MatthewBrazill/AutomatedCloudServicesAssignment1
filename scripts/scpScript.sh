#! /bin/bash

KEY=$1
INSTANCE_IP=$2

chmod 600 $KEY

# Wait for the HTTPD process to have started.
while [[ "$(ssh -o StrictHostKeyChecking=no -i $KEY ec2-user@${INSTANCE_IP} "pgrep httpd")" == "" ]]; do
    sleep 1
done

# Uploading files
scp -i $KEY ./webserver_files/index.html ec2-user@${INSTANCE_IP}:~/index.html > /dev/null 2> /dev/null
htmlId=$!
scp -i $KEY ./scripts/monitor.sh ec2-user@${INSTANCE_IP}:~/monitor.sh > /dev/null 2> /dev/null
shId=$!

# Wait for transfer to finish
wait $htmlId
wait $shId

# Move and run files as needed
ssh -i $KEY ec2-user@${INSTANCE_IP} "sudo mv /home/ec2-user/index.html /var/www/html/index.html" > /dev/null 2> /dev/null
ssh -i $KEY ec2-user@${INSTANCE_IP} "bash /home/ec2-user/monitor.sh" 2> /dev/null
