import json
import os
import boto3

sqs_client = boto3.client('sqs')

MESSAGE_QUEUE = os.environ.get('MESSAGE_QUEUE_NAME')


def handler(event, context):
     try:
          request = json.loads(event['body'])

          if not validate_message(request):
               print("Invalid message:", request)
               return {'statusCode': 400, 'body': 'Invalid message'}

          save_message(MESSAGE_QUEUE, request)
          return {'statusCode': 200, 'body': 'message sent successfully!'}

     except Exception as e:
          print(f"Error handling request: {e}")
          return {'statusCode': 500, 'body': 'Internal Server Error'}


def validate_message(message):
     metadata = message.get('metadata', {})
     return all(metadata.get(field) for field in ['message_time', 'company_id', 'message_id'])


def save_message(queue_url, request):
     try:
          sqs_client.send_message(
               QueueUrl=queue_url,
               MessageBody=json.dumps(request)
          )
     except Exception as e:
          print(f"Error sending messages to {queue_url}: {e}")
          raise
