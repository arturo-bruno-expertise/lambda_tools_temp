from typing import Dict

from aws_cdk.aws_apigateway import RestApi, LambdaIntegration
from constructs import Construct


class GoogleAdsApiGateway(Construct):
    api: RestApi = None

    def __init__(self, scope: Construct, identifier: str, lambdas: Dict) -> None:
        super().__init__(scope, identifier)

        self.api = RestApi(
            self,
            "ExpertiseToolsApi",
            rest_api_name="Expertise internal tools API",
            description="API with Expertise internal tools",
        )
        tools_resource = self.api.root.add_resource("tools")

        if "InvokeECSTasksFunction" in lambdas:
            ecs_tasks_resource = tools_resource.add_resource("ecs_tasks")

            ecs_tasks_resource.add_method(
                "GET", LambdaIntegration(lambdas["InvokeECSTasksFunction"])
            )
