import json
import os
import boto3
from botocore.exceptions import ClientError
from datetime import datetime

s3_client = boto3.resource('s3')
dynamodb_client = boto3.client('dynamodb')

def handler(event, context):
     for record in event['Records']:
          message = json.loads(record['body'])
          if not validate_message(message):
               print("Invalid message:", message)
               continue

          # Save message to S3
          save_to_s3(message)

          # Save message to DynamoDB
          save_to_dynamodb(message)


def validate_message(message):
     # Implement your validation logic here
     metadata = message.get('metadata', {})
     return all(metadata.get(field) for field in ['message_time', 'company_id', 'message_id'])


def save_to_s3(message):
     bucket_name_prefix = os.environ['BUCKET_NAME_PREFIX']
     company_id = message['metadata']['company_id']
     message_id = message['metadata']['message_id']

     bucket_name = f"{bucket_name_prefix}"
     object_key = f"{company_id}/{message_id}.json"

     # Using the resource method to get the S3 bucket
     bucket = s3_client.Bucket(bucket_name)
     bucket.put_object(Key=object_key, Body=json.dumps(message))


def save_to_dynamodb(message):
     try:
          dynamodb_client.put_item(
               TableName=os.environ['TABLE_NAME'],
               Item={
                    'message_id': {'S': message['metadata']['message_id']},
                    'company_id': {'S': message['metadata']['company_id']},
                    'message_time': {'S': message['metadata']['message_time']},
                    'order_id': {'S': message['data']['order_id']},
                    'order_time': {'S': message['data']['order_time']},
                    'order_amount': {'N': str(message['data']['order_amount'])},
               }
          )
          print("Message saved to DynamoDB")
     except ClientError as e:
          print(f"Error saving message to DynamoDB: {e}")
