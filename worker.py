#!/usr/bin/env python
import os
import boto
import json
import logging
import sys
import pprint
import ConfigParser
from django.template.loader import render_to_string
from django.conf import settings

settings.configure(DEBUG=True, TEMPLATE_Debug=True,
    TEMPLATE_DIRS=(
        "/Users/lfronius/git/squarepulse/templates",
        )
)

config = ConfigParser.ConfigParser()
config.read('worker.cfg')

logger = logging.getLogger('squarepulse')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

try:
    SQSQueue = config.get('squarepulse', 'sqsqueue')
except NoOptionError as e:
    logger.error(e)
    sys.exit(1)

if os.environ.get('AWS_CREDENTIAL_FILE') == None:
    if os.environ.get('AWS_ACCESS_KEY_ID') == None or os.environ.get('AWS_SECRET_ACCESS_KEY') == None:
        logger.error('AWS_ACCESS_KEY_ID/AWS_SECRET_ACCESS_KEY not in environment')
        sys.exit(1)

sqs = boto.connect_sqs()
ec2 = boto.connect_ec2()

if "region" in dict(config.items('squarepulse')):
    region = config.get('squarepulse', 'region')
    sqs = boto.sqs.connect_to_region(region)
    ec2 = boto.ec2.connect_to_region(region)

q = sqs.get_queue(SQSQueue)

q.set_message_class(boto.sqs.message.RawMessage)

def extract_message(rawMessage):
    body = json.loads(rawMessage.get_body())
    kv = [e.split('=', 1) for e in body['Message'].splitlines()]
    kv = [(k, v.strip("'")) for k, v in kv]
    message = dict(kv)
    return message

while True:
    try:
        rawMessage = q.read()
        if rawMessage is not None:
            message = extract_message(rawMessage)
            if any(message['ResourceStatus'] in s for s in config.sections()):
                if message['ResourceType'].lower().replace('::', '_') in dict(
                    config.items('squarepulse.' + message['ResourceStatus'])):
                    reservations = ec2.get_all_instances(instance_ids=[message['PhysicalResourceId']])
                    instance = reservations[0].instances[0].__dict__
                    template = config.get('squarepulse.' + message['ResourceStatus'],
                        message['ResourceType'].lower().replace('::', '_'))
                    try:
                        string = render_to_string(template, instance)
                        pprint.pprint(string)
                    except Exception as e:
                        logger.error(e, "Template not found")
            q.delete_message(rawMessage)

    except KeyboardInterrupt:
        sys.exit(0)

