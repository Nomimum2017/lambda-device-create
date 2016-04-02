# coding: utf-8
from __future__ import (absolute_import, division, print_function, unicode_literals)

import boto3
import uuid

thingName = str(uuid.uuid4())

def lambda_handler(event, context):

    iot = boto3.client('iot')
    dynamodb = boto3.resource('dynamodb')

    table = dynamodb.Table('devices')
    macaddr_check = table.get_item(
        Key={
            'macaddr': event['body']['macaddr']
        }
    )

    if 'Item' in macaddr_check:
        return "MAC address already exists. New device not created."
    else:
        createdevice = iot.create_thing(thingName=thingName,
                                        attributePayload={
                                            'attributes': {
                                                'string': 'string'
                                            }
                                        }
                                        )

        table.put_item(
            Item={
                'macaddr': event['body']['macaddr'],
                'deviceid': createdevice['thingName'],
            }
        )

