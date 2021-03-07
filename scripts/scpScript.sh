#! /bin/bash

KEY=$1
INSTANCE_IP=$2

chmod 600 $KEY

# Wait for the HTTPD process to have started.
while [[ "$(ssh -q -o StrictHostKeyChecking=no -i $KEY ec2-user@${INSTANCE_IP} "pgrep httpd")" == "" ]]; do
    sleep 1
done

# Uploading files
scp -q -i $KEY ./webserver_files/index.html ec2-user@${INSTANCE_IP}:~/index.html
htmlId=$!
scp -q -i $KEY ./scripts/monitor.sh ec2-user@${INSTANCE_IP}:~/monitor.sh
shId=$!

# Wait for transfer to finish
wait $htmlId
wait $shId

# Edit and move the index file to include the MetaData
ssh -q -i $KEY ec2-user@${INSTANCE_IP} 'sudo sed -q -i -e "s/instance_id/$(curl http://169.254.169.254/latest/meta-data/instance-id)/g" index.html'
ssh -q -i $KEY ec2-user@${INSTANCE_IP} 'sudo sed -q -i -e "s/instance_type/$(curl http://169.254.169.254/latest/meta-data/instance-type)/g" index.html'
ssh -q -i $KEY ec2-user@${INSTANCE_IP} 'sudo sed -q -i -e "s/public-ipv4/$(curl http://169.254.169.254/latest/meta-data/public-ipv4)/g" index.html'
ssh -q -i $KEY ec2-user@${INSTANCE_IP} 'sudo mv /home/ec2-user/index.html /var/www/html/index.html'

# Run the monitoring script
echo ""
ssh -i $KEY ec2-user@${INSTANCE_IP} "bash /home/ec2-user/monitor.sh"
