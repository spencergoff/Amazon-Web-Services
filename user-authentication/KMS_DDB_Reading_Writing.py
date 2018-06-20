#Source for encryption info: https://boyter.org/2017/12/simply-encrypt-string-boto3-python-aws-kms/

import boto3
import base64
from botocore.exceptions import ClientError

def encrypt(session, secret, alias):
    client = session.client('kms')
    ciphertext = client.encrypt(
        KeyId=alias,
        Plaintext=bytes(secret),
    )
    return base64.b64encode(ciphertext["CiphertextBlob"])

def lambda_handler(event, context):
    
    plain_text_password = event['password']
    username = event['username']
    key_alias = 'alias/ddb_key'
    table_name = 'GE_redo_authentication'
    
    session = boto3.session.Session()
    table = boto3.resource('dynamodb').Table(table_name)
    
    encrypted_password = encrypt(session, plain_text_password, key_alias)
    print('ENCRYPTED STRING: ' + encrypted_password)
    
    item = {
        'username':username,
        'password':encrypted_password
    }
    
    #check if item with the username already exists; if so, update password; else create new item
    entry = table.get_item(TableName=table_name, Key={'username':username})

    # if an entry with that username already exists, then update its corresponding password
    if 'Item' in entry:
        print('Item found. Updating password.')
        print("entry['Item']" + str(entry['Item']))
        response = table.update_item(
            Key={
                'username': username
            },
            UpdateExpression="set password = :p",
            ExpressionAttributeValues={
                ':p': encrypted_password
            },
            ReturnValues="UPDATED_NEW"
        )
    else:
        #if an entry with that username doesn't already exist, then create it
        print('Adding new item to table.')
        table.put_item(Item=item)
        new_entry = table.get_item(TableName=table_name, Key={'username':username})
        if 'Item' in new_entry:
            print('A new item was inserted in the table.')
        else:
            print('Failed to insert new item in table')

    return 'Function succeeded!'


'''def decrypt(session, secret):
    client = session.client('kms')
    plaintext = client.decrypt(
        CiphertextBlob=bytes(base64.b64decode(secret))
    )
    return plaintext["Plaintext"]'''
