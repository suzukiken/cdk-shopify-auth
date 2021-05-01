import * as cdk from '@aws-cdk/core'
import * as s3 from '@aws-cdk/aws-s3'

export class CdkshopifyouthS3Stack extends cdk.Stack {
  constructor(scope: cdk.Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props)
    
    const s3bucketname_exportname = this.node.tryGetContext('s3bucketname_exportname')
    
    const bucket = new s3.Bucket(this, 'bucket', {
      removalPolicy: cdk.RemovalPolicy.DESTROY
    })
    
    new cdk.CfnOutput(this, 'output', {
      exportName: s3bucketname_exportname,
      value: bucket.bucketName
    })
  }
}
