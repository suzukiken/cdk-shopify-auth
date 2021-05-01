#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from '@aws-cdk/core';
import { CdkshopifyouthStack } from '../lib/cdkshopifyouth-stack';
import { CdkshopifyouthS3Stack } from '../lib/cdkshopifyouth-s3-stack';


const app = new cdk.App();
new CdkshopifyouthS3Stack(app, 'CdkshopifyouthS3Stack', {
  env: { account: process.env.CDK_DEFAULT_ACCOUNT, region: process.env.CDK_DEFAULT_REGION }
});
new CdkshopifyouthStack(app, 'CdkshopifyouthStack', {
  env: { account: process.env.CDK_DEFAULT_ACCOUNT, region: process.env.CDK_DEFAULT_REGION }
});
