import boto3
import json
from boto3.dynamodb.conditions import Key
from decimal import Decimal

# Helper function to convert Decimal to regular Python types
def convert_decimal(obj):
    if isinstance(obj, list):
        return [convert_decimal(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: convert_decimal(v) for k, v in obj.items()}
    elif isinstance(obj, Decimal):
        return int(obj) if obj % 1 == 0 else float(obj)
    else:
        return obj

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('BooksTable')

    # Extract information from the request body
    try:
        body = json.loads(event['body'])
        title = body['Title']
        update_data = body['UpdateData']  # This should be a dictionary of attributes to update
    except (KeyError, json.JSONDecodeError) as e:
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': 'Invalid input: {}'.format(str(e))})
        }

    # Update the book in the DynamoDB table
    try:
        # Create the update expression dynamically
        update_expression = "SET " + ", ".join(f"#{key} = :{key}" for key in update_data.keys())
        expression_attribute_names = {f"#{key}": key for key in update_data.keys()}
        expression_attribute_values = {f":{key}": value for key, value in update_data.items()}

        response = table.update_item(
            Key={'Title': title},
            UpdateExpression=update_expression,
            ExpressionAttributeNames=expression_attribute_names,
            ExpressionAttributeValues=expression_attribute_values,
            ReturnValues="UPDATED_NEW"
        )

        # Convert the response attributes to standard Python types
        updated_attributes = convert_decimal(response.get('Attributes', {}))

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'message': 'Book updated successfully', 'updatedAttributes': updated_attributes})
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': str(e)})
        }
