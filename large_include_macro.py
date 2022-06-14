import boto3
import yaml
import logging
import os
import sys


def get_logger(name: str, log_level: str = 'info') -> logging.Logger:
    """Return a logger with the given name and logging level set"""
    handler = logging.StreamHandler(sys.stdout)
    log = logging.getLogger(name)
    log_level = log_level.lower()
    if log_level == 'debug':
        log.setLevel(logging.DEBUG)
        handler.setLevel(logging.DEBUG)
    elif log_level == 'warning':
        log.setLevel(logging.WARNING)
        handler.setLevel(logging.WARNING)
    elif log_level == 'error':
        log.setLevel(logging.ERROR)
        handler.setLevel(logging.ERROR)
    elif log_level == 'critical':
        log.setLevel(logging.CRITICAL)
        handler.setLevel(logging.CRITICAL)
    else:
        log.setLevel(logging.INFO)
        handler.setLevel(logging.INFO)

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(funcName)s - %(lineno)i - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    log.addHandler(handler)
    log.propagate = False
    return log


LOGGER = get_logger(os.path.basename(__file__), os.environ.get('LOG_LEVEL', 'info'))


def handle_template(request_id, template):
    LOGGER.info("Template before LargeInclude macro:")
    LOGGER.info(f"{template}")

    for name, resource in list(template.get("Resources", {}).items()):
        if resource["Type"] == "AWS::Serverless::Api":
            print("Found ApiGateway")
            props = resource["Properties"]
            def_body = props["DefinitionBody"]

            if "Transform" in def_body:
                transform = props["DefinitionBody"]["Transform"]
                if transform['Name'] == 'LargeInclude' and 'Parameters' in transform:
                    parameters = transform['Parameters']
                    bucket = parameters['Bucket']
                    key = parameters['Key']
                    local_file = '/tmp/include_me.yaml'

                    # Download S3 object at location
                    print("Downloading file")
                    s3 = boto3.client('s3')
                    print(bucket)
                    print(key)
                    print(local_file)
                    s3.download_file(bucket, key, local_file)

                    print("Opening file")
                    with open(local_file) as f:
                        yaml_object = yaml.safe_load(f)

                    template['Resources'][name]['Properties']['DefinitionBody'] = yaml_object

    LOGGER.info("Template after LargeInclude macro:")
    LOGGER.info(f"{template}")

    return template


def handler(event, context):
    print(event)
    print(event['requestId'])
    print(event['fragment'])
    try:
        template = handle_template(event["requestId"], event["fragment"])
    except Exception as e:
        LOGGER.error(f"Exception caught: {e}")
        return {
            "requestId": event["requestId"],
            "status": "failure",
            "fragment": event["fragment"],
        }

    return {
        "requestId": event["requestId"],
        "status": "success",
        "fragment": template,
    }
