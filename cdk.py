#!/usr/bin/env python3
import aws_cdk as cdk
from data_warehouse_common.schemas import EnvironmentVariables

from cdk.stack import GoogleAdsStack

env_vars = EnvironmentVariables(
    **{"account": "025737178121", "region": "us-east-2", "environment": "development"}
)

app = cdk.App()
GoogleAdsStack(
    app,
    "GoogleAdsStack",
    env_vars=env_vars,
    env=cdk.Environment(account=env_vars.account, region=env_vars.region),
)
app.synth()
