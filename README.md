# Assignment Review:

## Create and Launch EC2  Instance
I create a EC2 Instance into the default vpc with boto3 and configure it at startup with the generated security group and key pair as well as the same unique number as used in all other resources created during this run as a tag. This makes it easy to see which resources are used by what Instance. The index.html file is uploaded using scp and placed in the /var/www/html folder after the User Data creates the httpd process.

## Handling of instance settings (Security Group,  Key Name)
Using the boto3 ec2 resource I create a new Key Pair and Security Group. The name of them is auto generated to always be unique.

## Handling of User Data
There is a startupScript.sh file with the Users Data in that is loaded in and used. This makes it easily configurable and changeable.

## S3 Bucket Creation and Image Upload
Again using the unique number that is used with all other resources a new bucket that is guaranteed to be available is created. All files in the webserver_files/bucket folder are then uploaded. The image.jpg file is updated from the given link in the Assignment details at the start of the program.

## Update web page with instance metadata using SSH remote command
The scpScript.sh file in the scripts folder runs several ssh sed commands that change the index.html file to replace the placeholder keywords with the culred instance metadata. The index.html file is also moved to the /var/www/html folder after editing.

## Update web page with S3 URL
Before the index.html file is uploaded to the EC2 Instance it is modified to replace the first image tag in it with the image tag linking to the image in the bucket using the newly created buckets link.

## Monitoring
After all files are uploaded, edited and placed in the correct folder the scpScript.sh file uploads and executes the monitor.sh script to get the monitoring data from the instance in displays it to the user.

## Additional functionality
The whole program is executable without any user input or interaction and creates all the needed resources itself, meaning it can be run successfully in anw AWS environment with no setup needed. A custom bucket name can be passed on to the program with the argument --bucket_name and a help interface is available at --help or -h.

## Non-Functional: Exceptions and handling error codes, testing, logging, readability
The whole code is logged to the logs/logfile.log file which operates at the information level and the program prints error messages to the user on screen. The code is tested and debugged by myself but no unittest was done. The code is also thoroughly commented and structured so its easy to read.

