from aws_cdk import Stack, Tags, Environment
from constructs import Construct
from data_warehouse_common.schemas import EnvironmentVariables

from .api_gateway import GoogleAdsApiGateway
from .lambdas import GoogleAdsLambdas


class ExpertiseToolsStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        env: Environment,
        env_vars: EnvironmentVariables = None,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, env=env)

        tools_lambdas = GoogleAdsLambdas(
            self, "GoogleAdsLambdas", env_vars=env_vars
        )

        GoogleAdsApiGateway(
            self, "GoogleAdsAPIGateway", lambdas=google_ads_lambdas.lambdas
        )

        Tags.of(scope).add("developer", "arturo@expertise.com")
