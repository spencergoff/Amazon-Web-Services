import os
import boto3
import base64
from boto3.dynamodb.conditions import Key, Attr
import botocore.vendored.requests.api as requests

def decrypt(session, secret):
    client = session.client('kms')
    plaintext = client.decrypt(
        CiphertextBlob=bytes(base64.b64decode(secret))
    )
    return plaintext["Plaintext"]

def lambda_handler(event, context):
    
    session = boto3.session.Session()
    dynamodb = boto3.resource('dynamodb')
    authentication_table_name = 'GE_redo_authentication'
    authorization_table = dynamodb.Table('GE_redo_authorization')
    authentication_table = dynamodb.Table(authentication_table_name)
    
    # Extract the username, password, and resource from the message
    
    message = str(event['message'])
    password = message.split('password>')[1][:-2]
    username = message.split('username>')[1][:-2]
    resource = message.split('resource>')[1][:-2]
    
    print('MESSAGE: ' + message)
    print('PASSWORD: ' + str(password))
    print('USERNAME: ' + str(username))
    print('RESOURCE: ' + str(resource))
    
    # Authenticate user with encrypted DDB
    
    entry = authentication_table.get_item(TableName=authentication_table_name, Key={'username':username})
    
    if 'Item' in entry:
        #print('entry["Item"]["password"]: ' + str(entry['Item']['password']))
        password_from_table = entry['Item']['password']
        decrypted_password_from_table = decrypt(session,password_from_table)
        decrypted_password_from_table = decrypted_password_from_table.decode('utf-8')
        print('type(decrypted_password_from_table): ' + str(type(decrypted_password_from_table)))
        print('attempted password: ' + str(password))
        print('decrypted_password_from_table: ' + str(decrypted_password_from_table))
        if password == decrypted_password_from_table:
            print('User has been authenticated.')
        else:
            print('Incorrect password')
            return 'Incorrect password'
    else:
        print('User is NOT VALID')
        return 'Invalid User'

    # Authorize user with unencrypted DDB
    
    allowed_resources = authorization_table.get_item(Key={'username': username})['Item']['allowed_resources']
    allowed_resources = allowed_resources.split(',')
    print('allowed_resources: ' + str(allowed_resources))
    if resource not in allowed_resources:
        return 'USER NOT AUTHORIZED TO ACCESS RESOURCE'
    
    # Forward message to endpoint
    response = requests.request('GET', 'https://postman-echo.com/get?foo1=bar1', params={'foo1': message})
    print('dummy echo api response.text: ' + str(response.text))

    return_string = 'Success! Here is your API response: ' + str(response.text)
    return return_string

'''call this function via the API like this: https://cn3p4e245e.execute-api.us-east-1.amazonaws.com/prod/request?message=<note><to>Tove</to><username>testuser1</username><testpassword>testpassword</password><resource>testresource2</resource></note>'''
