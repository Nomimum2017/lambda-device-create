# coding: utf-8
from __future__ import (absolute_import, division, print_function, unicode_literals)

import boto3
import uuid

thingName = str(uuid.uuid4())

def lambda_handler(event, context):

    iot = boto3.client('iot')
    createdevice = iot.create_thing(thingName=thingName,
                     attributePayload={
                         'attributes': {
                             'string': 'string'
                         }
                     }
                )

    dynamodb = boto3.resource('dynamodb')

    table = dynamodb.Table('devices')

    table.put_item(
        Item={
            'macaddr': event['body']['macaddr'],
            'deviceid': createdevice['thingName'],
        }
    )