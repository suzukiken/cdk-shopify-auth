import urllib.parse
import hashlib
import hmac
import os
import uuid
import boto3

s3 = boto3.client('s3')

scope_list = (
  'read_products',
#  'read_product_listings',
  'read_orders',
#  'read_all_orders',
  'read_inventory',
#  'write_inventory',
  'read_locations',
  'read_fulfillments',
#  'write_fulfillments',
  'read_assigned_fulfillment_orders',
#  'write_assigned_fulfillment_orders',
  'read_shipping',
#  'write_shipping',
#  'read_checkouts',
#  'write_checkouts',
)

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
    
  hmac_string = event['queryStringParameters']['hmac']
  querystring_dir = event['queryStringParameters']
  del querystring_dir['hmac']
  
  querystring = urllib.parse.urlencode(querystring_dir)
  
  print(querystring)
  print(hmac_string)
  
  # m = hashlib.sha256()
  # m.update(querystring.encode('utf-8'))
  # print(m.hexdigest())
  
  signature = hmac.new(
    os.environ.get('SECRET_KEY').encode('utf-8'),
    msg=querystring.encode('utf-8'),
    digestmod=hashlib.sha256
  ).hexdigest()
  
  if not hmac_string == signature:
    raise ValueError('hmac {} is not same as {}'.format(hmac_string, signature))

  nonce = str(uuid.uuid1())
  scopes = ','.join(scope_list)
  shop = event['queryStringParameters']['shop']
  
  if not shop.endswith('.myshopify.com'):
    raise ValueError('shop is not endswith .myshopify.com')
  
  shop = shop.replace('.myshopify.com', '')
  
  response = s3.put_object(
    Bucket=os.environ.get('S3_BUCKETNAME'),
    Key='{}/{}'.format(os.environ.get('SHOPIFY_APPNAME'),nonce),
    Body=shop.encode('utf-8')
  )
  
  print(response)
  
  api_key = os.environ.get('API_KEY')
  redirect_uri = os.environ.get('REDIRECT_URI')
  access_mode = ''
  redirect_uri_quoted = urllib.parse.quote(redirect_uri)
  
  redirect = f'https://{shop}.myshopify.com/admin/oauth/authorize?client_id={api_key}&scope={scopes}&redirect_uri={redirect_uri_quoted}&state={nonce}&grant_options[]={access_mode}'
  
  print(redirect)
  
  return {
    "statusCode": 302,
    "headers": {
      "Location": redirect
    }
  }
