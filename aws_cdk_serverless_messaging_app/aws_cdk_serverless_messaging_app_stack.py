from aws_cdk import (
    Duration,
    Stack,
    aws_sqs as _sqs,
    aws_lambda as _lambda,
    aws_lambda_event_sources as _lambda_event_sources,
    aws_s3 as _s3,
    aws_dynamodb as _dynamodb,
    aws_apigateway as _apigateway
)
from constructs import Construct


class AwsCdkServerlessMessagingAppStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create SQS Queue
        message_queue = _sqs.Queue(
            self, "AwsCdkServerlessMessageAppQueue",
            visibility_timeout=Duration.seconds(300),
        )

        # Create API Gateway
        message_api = _apigateway.RestApi(
            self, 'MessageApi',
            rest_api_name='message-api',
            description='API for manage messages'
        )

        # Create DynamoDB Table
        message_table = _dynamodb.Table(
            self, 'OrderMessageTable',
            table_name='order_message',
            partition_key=_dynamodb.Attribute(
                name='message_id',
                type=_dynamodb.AttributeType.STRING
            ),
            billing_mode=_dynamodb.BillingMode.PAY_PER_REQUEST
        )

        # Create S3 Bucket
        message_bucket = _s3.Bucket(
            self, id='s3bucket', 
            bucket_name='messages-storage-bucket', 
            versioned=True, 
            encryption=_s3.BucketEncryption.S3_MANAGED
        )
        



        # Post Message Function
        post_message_lambda = _lambda.Function(
            self, id='PostMessageFunction', 
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler='message.post.handler.handler',
            code=_lambda.Code.from_asset('lambda'),
            environment={
                "MESSAGE_QUEUE_NAME": message_queue.queue_name
            }
        )
        message_queue.grant_send_messages(post_message_lambda)
        post_message_resource = message_api.root.add_resource('post-message')
        post_message_lambda_integration = _apigateway.LambdaIntegration(
            handler=post_message_lambda
        )
        post_message_resource.add_method('POST', post_message_lambda_integration)




        # Save Message Function
        save_message_lambda = _lambda.Function(
            self, id='SaveMessageFunction', 
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler='message.save.handler.handler',
            code=_lambda.Code.from_asset('lambda'),
            environment={
                "BUCKET_NAME_PREFIX": "messages-storage-bucket",
                "TABLE_NAME": "order_message"
            }
        )
        message_event_source = _lambda_event_sources.SqsEventSource(message_queue) # Create Event Source
        save_message_lambda.add_event_source(message_event_source) # Add SQS Event source to lambda
        message_table.grant_write_data(save_message_lambda)
        message_bucket.grant_read_write(save_message_lambda)




        # Get Message Function
        get_message_lambda = _lambda.Function(
            self, id='GetMessageFunction', 
            handler='message.get.handler.handler',
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset('lambda'),
            environment={
                "TABLE_NAME": "order_message"
            }
        )
        message_table.grant_read_data(get_message_lambda)
        # Define the resource with the {message_id} path parameter
        message_resource = message_api.root.add_resource('message')
        message_id_resource = message_resource.add_resource('{message_id}')
        get_message_api_lambda_integration = _apigateway.LambdaIntegration(
            handler=get_message_lambda
        )
        message_id_resource.add_method('GET', get_message_api_lambda_integration)



