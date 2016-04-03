# coding: utf-8
from __future__ import (absolute_import, division, print_function, unicode_literals)

import boto3
import uuid

thingName = str(uuid.uuid4())

def lambda_handler(event, context):

    macAddr = event['body']['macAddr']

    iot = boto3.client('iot')
    dynamodb = boto3.resource('dynamodb')
    mapTable = dynamodb.Table('device-map')
    certTable = dynamodb.Table('device-certs')

    macAddrCheck = mapTable.get_item(
        Key={
            'macAddr': macAddr
        }
    )

    if 'Item' in macAddrCheck:
        print("macAddrCheck output: ", macAddrCheck['ResponseMetadata'])
        return { "message": "MAC address already exists. New device not created." }
    else:
        print("macAddrCheck output: ", macAddrCheck['ResponseMetadata'])
        createDevice = iot.create_thing(thingName=thingName)
        print("createDevice output: ", createDevice['ResponseMetadata'])

        insertDevice = mapTable.put_item(
            Item={
                'macAddr': macAddr,
                'deviceId': createDevice['thingName'],
            }
        )
        print("insertDevice output: ", insertDevice['ResponseMetadata'])

    createCert = iot.create_keys_and_certificate(
        setAsActive=True
    )
    print("createCert output: ", createCert['ResponseMetadata'])

    attachCert = iot.attach_thing_principal(
        thingName= createDevice['thingName'],
        principal= createCert['certificateArn']
    )
    print("attachCert output: ", attachCert['ResponseMetadata'])

    insertCert = certTable.put_item(
        Item={
            'deviceId': createDevice['thingName'],
            'certificatePem': createCert['certificatePem'],
            'PublicKey': createCert['keyPair']['PublicKey'],
            'PrivateKey': createCert['keyPair']['PrivateKey'],
        }
    )
    print("insertCert output: ", insertCert['ResponseMetadata'])

    return {"message": "Device created."}