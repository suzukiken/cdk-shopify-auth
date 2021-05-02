import urllib.parse
import urllib.request
import hashlib
import hmac
import os
import boto3
import json

s3 = boto3.client('s3')

def lambda_handler(event, context):
    
  print(event)
  
  if not 'queryStringParameters' in event:
    raise ValueError('No querystrings in event')
    
  if not 'hmac' in event['queryStringParameters']:
    raise ValueError('No hmac in querystrings')

  if not 'shop' in event['queryStringParameters']:
    raise ValueError('No shop in querystrings')
    
  if not 'timestamp' in event['queryStringParameters']:
    raise ValueError('No timestamp in querystrings')

  if not 'state' in event['queryStringParameters']:
    raise ValueError('No state in querystrings')

  if not 'code' in event['queryStringParameters']:
    raise ValueError('No code in querystrings')

  hmac_string = event['queryStringParameters']['hmac']
  querystring_dir = event['queryStringParameters']
  del querystring_dir['hmac']
  
  querystring = urllib.parse.urlencode(querystring_dir)
  
  print(querystring)
  print(hmac_string)
  
  signature = hmac.new(
    os.environ.get('SECRET_KEY').encode('utf-8'),
    msg=querystring.encode('utf-8'),
    digestmod=hashlib.sha256
  ).hexdigest()
  
  if not hmac_string == signature:
    raise ValueError('hmac {} is not same as {}'.format(hmac_string, signature))
  
  nonce = event['queryStringParameters']['state']
  
  response = s3.get_object(
    Bucket=os.environ.get('S3_BUCKETNAME'),
    Key='{}/{}'.format(os.environ.get('SHOPIFY_APPNAME'), nonce)
  )
  
  print(response)
  
  shop = event['queryStringParameters']['shop']
  
  qs_shopname = shop.replace('.myshopify.com', '')
  saved_shopname = response['Body'].read().decode('utf8')
  
  if not qs_shopname == saved_shopname:
    raise ValueError('{} is not same as {}'.format(qs_shopname, saved_shopname))

  auth_url = 'https://{}.myshopify.com/admin/oauth/access_token'.format(qs_shopname)
  data = {
    'client_id': os.environ.get('API_KEY'),
    'client_secret': os.environ.get('SECRET_KEY'),
    'code': event['queryStringParameters']['code']
  }
  encode_data = urllib.parse.urlencode(data).encode()
  req = urllib.request.Request(auth_url, data=encode_data, method='POST')
  with urllib.request.urlopen(req) as res:
    res_body = json.loads(res.read())
    print(res_body)
  
  response = s3.put_object(
    Bucket=os.environ.get('S3_BUCKETNAME'),
    Key='{}/{}'.format(os.environ.get('SHOPIFY_APPNAME'), shop),
    Body=res_body['access_token'].encode('utf8')
  )
  
  print(response)
  
  return {
    'headers': {
      'Content-Type': 'text/plain'
    },
    'statusCode': 200,
    'body': 'done'
  }