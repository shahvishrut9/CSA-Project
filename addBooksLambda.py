import boto3
import json
from decimal import Decimal

# Initialize the DynamoDB client
dynamodb = boto3.resource('dynamodb')

# Replace 'BooksTable' with your actual DynamoDB table name
TABLE_NAME = 'BooksTable'
table = dynamodb.Table(TABLE_NAME)

# Helper function to handle Decimal objects
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj) if obj % 1 else int(obj)
        return super(DecimalEncoder, self).default(obj)

def lambda_handler(event, context):
    try:
        # Parse the request body
        body = json.loads(event['body'])
        
        # Extract book details
        title = body.get('Title')
        authors = body.get('Authors')
        publisher = body.get('Publisher')
        year = body.get('Year')

        # Ensure all fields are provided
        if not all([title, authors, publisher, year]):
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Missing required fields'})
            }
        
        # Add the book to the DynamoDB table
        table.put_item(
            Item={
                'Title': title,
                'Authors': authors,
                'Publisher': publisher,
                'Year': int(year)
            }
        )

        return {
            'statusCode': 201,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'message': 'Book added successfully'})
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
