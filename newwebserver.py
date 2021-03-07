#! usr/bin/env python3


# Imports
import uuid
import sys
import boto3
import logging
import os
import subprocess

# Resources
s3 = boto3.resource("s3")
ec2 = boto3.resource("ec2")

# Logging Configuration
if not os.path.exists("./logs"):
    os.makedirs("./logs")
logging.basicConfig(
    format="%(asctime)s %(levelname)s: %(message)s",
    filename="./logs/logfile.log",
    level="INFO"
)

# Global Variables

# An ID for the creation process. This ID is used to group all the resources
# by giving them all the process id as a key.
global processID
processID = str(uuid.uuid4())
logging.info("Creating session UUID: %s", processID)

# The AWS account ID that identifies the user. This is needed for the cleanup
# process.
global accountID
accountID = str(boto3.client("sts").get_caller_identity()["Account"])
logging.info("Finding aws account ID: %s", accountID)

# TODO
# 1. Add more extensive logging


# Main function
def main():
    """The main function to start all the processes and gather user input.

    After gathering the details from the user the program starts all the
    individual task off, such as the creation of the S3 Bucket, the creation
    of the EC2 instance and the launching of the Apache server. If the user
    doesn't provide an input a generic one is generated.
    """

    # Variables
    startupScript = open(f"./scripts/startupScript.sh", "r").read()

    # Getting arguments from user. If there are none defaults are used.
    if "--bucket_name" in sys.argv:
        bucketName = sys.argv[sys.argv.index("-bucket_name") + 1]
        logging.info("Bucket name set to '%s'.", bucketName)
    else:
        bucketName = "webserver-assignment-bucket-brazill"

    if "--help" in sys.argv:
        doHelp()
        return

    # Create the Instance
    instanceReady = createInstance(startupScript)

    # Create the Bucket
    bucketReady = createBucket(bucketName)

    if instanceReady == True == bucketReady:
        return True


# Function to create the Bucket
def createBucket(bucketName: str) -> bool:
    """This function creates the S3 Bucket.

    This function creates the Bucket that contains the image files needed for
    the static webserver that will run on the EC2 instance.
    """

    try:
        # Creating the S3 Bucket
        logging.info("Creating the S3 bucket...")
        bucket = s3.create_bucket(
            Bucket=bucketName,
            CreateBucketConfiguration={
                "LocationConstraint": "eu-west-1"
            }
        )

    except Exception as err:
        if err.response["Error"]["Code"] == "BucketAlreadyOwnedByYou":
            logging.warning("Bucket already exists but belongs to you.")
            bucket = s3.Bucket(bucketName)
        else:
            logging.error("Bucket creation failed: " + str(err))
            return

    else:
        logging.info("Bucket '%s' created successfully.", str(bucket.name))

    return fillBucket(bucket)


def fillBucket(bucket: object) -> bool:
    """This function fills the S3 bucket

    After the bucket was created it needs to be filled with the necessary
    files to support the webserver. To have files be uploaded they need to be
    in the "bucket" subfolder in the webfiles folder.
    """

    # Uploading files to the bucket
    try:
        logging.info("Uploading webserver files to S3 Bucket.")
        for file in os.scandir("./webserver_files/bucket"):
            bucket.upload_file(
                "./webserver_files/bucket/"+file.name,
                file.name,
                ExtraArgs={'ACL': 'public-read'}
            )

        # Use the S3 bucket as a way of putting the index file onto the EC2
        # instance by uploading it from here and then downloading it in the
        # startup script.
        bucket.upload_file(
            "./webserver_files/index.html",
            "index.html",
            ExtraArgs={'ACL': 'public-read'}
        )

    except Exception as err:
        logging.error("Uploading failed: " + str(err))
        return False

    logging.info("Uploading complete.")
    return True


# Function to create the instance
def createInstance(startupScript: str) -> bool:
    """This function creates the EC2 Instance

    To host the Webserver the EC2 instance is created to run everything.
    """

    try:
        # Create Authentication Key
        logging.info("Creating a new Key Pair...")
        keyPair = ec2.create_key_pair(
            KeyName=f"webserver-key-{processID}",
            TagSpecifications=[
                {
                    "ResourceType": "key-pair",
                    "Tags": [
                        {
                            "Key": processID,
                            "Value": ""
                        },
                    ]
                },
            ]
        )
        keyFile = open(keyPair.key_name + ".pem", "w")
        keyFile.write(keyPair.key_material)

    except Exception as err:
        logging.error("Key Pair creation failed: " + str(err))
        return False
    else:
        logging.info("Key Pair '%s' created successfully.", keyPair.key_name)

    try:
        # Create Security Group
        logging.info("Creating a new Security Group...")
        securityGroup = ec2.create_security_group(
            Description=f"A autogenerated security group for the webserver-{processID}.",
            GroupName=f"webserver-security-group-{processID}",
            TagSpecifications=[
                {
                    "ResourceType": "security-group",
                    "Tags": [
                        {
                            "Key": processID,
                            "Value": ""
                        },
                    ]
                },
            ]
        )
        # Allow HTTP access for viewing of the webserver
        securityGroup.authorize_ingress(IpPermissions=[{
            "FromPort": 80,
            "ToPort": 80,
            "IpProtocol": "tcp",
            "IpRanges": [
                {
                    "CidrIp": "0.0.0.0/0",
                    "Description": "Allow HTTP access for viewing of the webserver"
                }
            ]}])
        # Allow HTTPs access for viewing of the webserver
        securityGroup.authorize_ingress(IpPermissions=[{
            "FromPort": 443,
            "ToPort": 443,
            "IpProtocol": "tcp",
            "IpRanges": [
                {
                    "CidrIp": "0.0.0.0/0",
                    "Description": "Allow HTTPs access for viewing of the webserver"
                }
            ]}])
        # Allow SSH access for configuration of the webserver
        securityGroup.authorize_ingress(IpPermissions=[{
            "FromPort": 22,
            "ToPort": 22,
            "IpProtocol": "tcp",
            "IpRanges": [
                {
                    "CidrIp": "0.0.0.0/0",
                    "Description": "Allow SSH access for configuration of the webserver"
                }
            ]}])

    except Exception as err:
        logging.error("Security Group creation failed: " + str(err))
        return False
    else:
        logging.info("Security Group '%s' created successfully.", securityGroup.group_name)

    try:
        # Creating the EC2 Instance
        logging.info("Creating the EC2 Instance...")
        instance = ec2.create_instances(
            ImageId="ami-096f43ef67d75e998",
            InstanceType="t2.nano",
            KeyName=keyPair.key_name,
            MaxCount=1,
            MinCount=1,
            Monitoring={
                "Enabled": False
            },
            SecurityGroups=[securityGroup.group_name],
            UserData=startupScript,
            DisableApiTermination=False,
            EbsOptimized=False,
            InstanceInitiatedShutdownBehavior="terminate",
            TagSpecifications=[
                {
                    "ResourceType": "instance",
                    "Tags": [
                        {
                            "Key": processID,
                            "Value": ""
                        }
                    ]
                }
            ]
        )[0]
        instance.wait_until_running()
        instance.reload()

    except Exception as err:
        logging.error("Instance creation failed: " + str(err))
        return False
    else:
        logging.info("Instance created successfully on IP: %s", instance.public_ip_address)
        print(f"Webserver running at: http://{instance.public_dns_name}")

    try:
        subprocess.run(["./scripts/scpScript.sh", keyPair.key_name, instance.public_ip_address])

    except Exception as err:
        logging.error("Instance setup failed: " + str(err))
        return False

    return True


# Function to display help interface
def doHelp():
    return


# Starting the program
logging.info("Starting program...")
main()
logging.info("Program complete. The web server should now be active.\n\n\n")
