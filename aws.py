import boto3

dynamodb = boto3.resource('dynamodb')

table = dynamodb.Table('Google_YNAB_info')
response = table.get_item(
    Key={
        'user': '1'
    }
)
get_item = response['Item']

s3 = boto3.client('s3')
