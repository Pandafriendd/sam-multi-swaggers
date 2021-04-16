#!/bin/sh

# IMPORTANT: Bucket names must be unique for all AWS users.
BUCKET="pet-store-api-deployment-workspace-666-jasdsjnfsjfd"

# Delete CloudFormation Stack
aws cloudformation delete-stack \
    --stack-name pet-store-stack \
    --region us-east-1

# Delete non-empty bucket
aws s3 rb s3://$BUCKET --region us-east-1 --force
