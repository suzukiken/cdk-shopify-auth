import * as cdk from '@aws-cdk/core'
import * as lambda from '@aws-cdk/aws-lambda'
import * as apigateway from '@aws-cdk/aws-apigateway'
import { PythonFunction } from "@aws-cdk/aws-lambda-python"
import * as acm from '@aws-cdk/aws-certificatemanager'
import * as route53 from '@aws-cdk/aws-route53'
import * as targets from '@aws-cdk/aws-route53-targets'
import * as sm from '@aws-cdk/aws-secretsmanager'
import * as s3 from '@aws-cdk/aws-s3'

export class CdkshopifyouthStack extends cdk.Stack {
  constructor(scope: cdk.Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props)
    
    const basename = id.toLowerCase().replace('stock', '')
    const shopify_app_secret = sm.Secret.fromSecretNameV2(this, "shopify_app_secret", this.node.tryGetContext('shopify_app_secretname'))
    
    const API_KEY = shopify_app_secret.secretValueFromJson("API_KEY").toString()
    const SECRET_KEY = shopify_app_secret.secretValueFromJson("SECRET_KEY").toString()
    const REDIRECT_URI = shopify_app_secret.secretValueFromJson("REDIRECT_URI").toString()
    
    const DOMAIN = this.node.tryGetContext('domain')
    const SUBDOMAIN = this.node.tryGetContext('subdomain')
    const SHOPIFY_APPNAME = this.node.tryGetContext('shopify_appname')

    const ACMARN = cdk.Fn.importValue(this.node.tryGetContext('tokyo_acmarn_exportname'))

    const bucket_name = cdk.Fn.importValue(this.node.tryGetContext('s3bucketname_exportname'))
    const buckt = s3.Bucket.fromBucketName(this, 'bucket', bucket_name)

    const askforperm = new PythonFunction(this, 'askforperm', {
      entry: 'lambda',
      index: 'askforpermission.py',
      handler: 'lambda_handler',
      runtime: lambda.Runtime.PYTHON_3_8,
      environment: {
        API_KEY: API_KEY,
        SECRET_KEY: SECRET_KEY,
        REDIRECT_URI: REDIRECT_URI,
        S3_BUCKETNAME: buckt.bucketName,
        SHOPIFY_APPNAME: SHOPIFY_APPNAME
      }
    })
    
    const installation = new PythonFunction(this, 'installation', {
      entry: 'lambda',
      index: 'confirminstallation.py',
      handler: 'lambda_handler',
      runtime: lambda.Runtime.PYTHON_3_8,
      environment: {
        API_KEY: API_KEY,
        SECRET_KEY: SECRET_KEY,
        S3_BUCKETNAME: buckt.bucketName,
        SHOPIFY_APPNAME: SHOPIFY_APPNAME
      }
    })
    
    buckt.grantWrite(askforperm)
    buckt.grantReadWrite(installation)
    
    const api = new apigateway.RestApi(this, 'api', { 
      restApiName: basename + '-api',
      domainName: {
        domainName: SUBDOMAIN + '.' + DOMAIN,
        certificate: acm.Certificate.fromCertificateArn(this, 'cm', ACMARN)
      }
    })
    
    const record = new route53.ARecord(this, 'arecord', {
      zone: route53.HostedZone.fromLookup(this, 'zone', {
        domainName: DOMAIN
      }),
      target: route53.RecordTarget.fromAlias(new targets.ApiGateway(api)),
      recordName: SUBDOMAIN,
    })
    
    record.applyRemovalPolicy(cdk.RemovalPolicy.DESTROY)

    const askperm_integration = new apigateway.LambdaIntegration(askforperm)
    
    api.root.addMethod('GET', askperm_integration)

    const installation_integration = new apigateway.LambdaIntegration(installation)
    
    const redirect = api.root.addResource('redirect')
    
    redirect.addMethod('GET', installation_integration)
    
  }
}
