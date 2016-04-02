# coding: utf-8
from __future__ import (absolute_import, division, print_function, unicode_literals)

import boto3
import uuid

thingName = str(uuid.uuid4())
tevent = { "body" : { "macaddr": "abc1234f" }}

def lambda_handler(event, context):

    macAddr = tevent['body']['macaddr']

    iot = boto3.client('iot')
    dynamodb = boto3.resource('dynamodb')

    table = dynamodb.Table('devices')
    macaddrCheck = table.get_item(
        Key={
            'macaddr': macAddr
        }
    )

    if 'Item' in macaddrCheck:
        return "MAC address already exists. New device not created."
    else:
        print("macaddrCheck output: " + str(macaddrCheck.get()))
        createDevice = iot.create_thing(thingName=thingName,
                                        attributePayload={
                                            'attributes': {
                                                'string': 'string'
                                            }
                                        }
                                        )
        print("createDevice output: " + str(createDevice.get()))

        insertDevice = table.put_item(
            Item={
                'macaddr': macAddr,
                'deviceid': createDevice['thingName'],
            }
        )
        print("insertDevice output: " + str(insertDevice.get()))

