import json
import os
import boto3
from botocore.exceptions import ClientError

dynamodb_client = boto3.client('dynamodb')

def handler(event, context):
     try:
          # Get message_id from path parameters
          message_id = event['pathParameters']['message_id']

          # Get message from DynamoDB using the message_id
          message = get_message_from_dynamodb(message_id)

          if message:
               return {
                    'statusCode': 200,
                    'body': json.dumps(message)
               }
          else:
               return {
                    'statusCode': 404,
                    'body': json.dumps({'error': f"Message with ID {message_id} not found"})
               }

     except Exception as e:
          print(f"Error: {e}")
          return {
               'statusCode': 500,
               'body': json.dumps({'error': 'Internal Server Error'})
          }


def get_message_from_dynamodb(message_id):
     try:
          response = dynamodb_client.get_item(
               TableName=os.environ['TABLE_NAME'],
               Key={
                    'message_id': {'S': message_id}
               }
          )
          item = response.get('Item')

          if item:
               # Assuming the DynamoDB item structure is the same as when saving
               message = {
                    'metadata': {
                         'message_id': item['message_id']['S'],
                         'company_id': item['company_id']['S'],
                         'message_time': item['message_time']['S'],
                    },
                    'data': {
                         'order_id': item['order_id']['S'],
                         'order_time': item['order_time']['S'],
                         'order_amount': float(item['order_amount']['N']),
                    }
               }

               return message
          else:
               print(f"Message with ID {message_id} not found in DynamoDB")
               return None

     except ClientError as e:
          print(f"Error getting message from DynamoDB: {e}")
          return None
