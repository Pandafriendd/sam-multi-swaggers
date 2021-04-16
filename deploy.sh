#!/bin/sh

# IMPORTANT: Bucket names must be unique for all AWS users.
BUCKET="pet-store-api-deployment-workspace-666-jasdsjnfsjfd"

# Creates your deployment bucket if it doesn't exist yet.
aws s3 mb s3://$BUCKET --region us-east-1 

# Uploads files to S3 bucket and creates CloudFormation template
sam package \
    --template-file template.yaml \
    --s3-bucket $BUCKET \
    --output-template-file package.yaml \
    --region us-east-1

# Deploys your stack
sam deploy \
    --template-file package.yaml \
    --stack-name pet-store-stack \
    --capabilities CAPABILITY_IAM \
    --region us-east-1 --debug
