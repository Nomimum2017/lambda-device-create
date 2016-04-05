# coding: utf-8
from __future__ import (absolute_import, division, print_function, unicode_literals)

import boto3
import uuid
import re

def lambda_handler(event, context):

    deviceId = str(uuid.uuid4())
    inputMacAddr = event['body']['macAddr']

    macAddr = re.sub(':', '', inputMacAddr.lower())
    macAddr = re.sub('-', '', macAddr)
    macAddr = re.sub('\.', '', macAddr)
    macAddr = re.sub(' ', '', macAddr)

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
        createDevice = iot.create_thing(thingName=deviceId)
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

    parsedCertificatePem = []
    for line in createCert['certificatePem']:
        parsedline = line.rstrip('\n')
        parsedCertificatePem.append(parsedline)
        certficatePem = ''.join(parsedCertificatePem)

    parsedPublicKey = []
    for line in createCert['keyPair']['PublicKey']:
        parsedline = line.rstrip('\n')
        parsedPublicKey.append(parsedline)
        publicKey = ''.join(parsedPublicKey)

    parsedPrivateKey = []
    for line in createCert['keyPair']['PublicKey']:
        parsedline = line.rstrip('\n')
        parsedPrivateKey.append(parsedline)
        privateKey = ''.join(parsedPrivateKey)


    attachCert = iot.attach_thing_principal(
        thingName= createDevice['thingName'],
        principal= createCert['certificateArn']
    )
    print("attachCert output: ", attachCert['ResponseMetadata'])

    insertCert = certTable.put_item(
        Item={
            'deviceId': createDevice['thingName'],
            'certificatePem': certficatePem,
            'publicKey': publicKey,
            'privateKey': privateKey,
        }
    )
    print("insertCert output: ", insertCert['ResponseMetadata'])

    return {"message": "Device created."}
