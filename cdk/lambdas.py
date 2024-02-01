import os
from typing import Dict

from aws_cdk import Duration
from aws_cdk import aws_iam as iam
from aws_cdk.aws_lambda import DockerImageCode, DockerImageFunction
from constructs import Construct
from data_warehouse_common.schemas import EnvironmentVariables


class ExpertiseToolsLambdas(Construct):
    lambdas: Dict

    def __init__(
        self, scope: Construct, identifier: str, env_vars: EnvironmentVariables
    ) -> None:
        super().__init__(scope, identifier)

        expertise_lambdas_role = iam.Role.from_role_arn(
            self,
            "ExpertiseLambdasRoles",
            role_arn="arn:aws:iam::025737178121:role/ExpertiseLambdas",
            mutable=False,
        )

        build_arguments = {
            "ENV": env_vars.environment,
            "AWS_REGION": env_vars.region,
            "AWS_ACCOUNT": env_vars.account,
            "AWS_ACCESS_KEY_ID": os.getenv("AWS_ACCESS_KEY_ID"),
            "AWS_SECRET_ACCESS_KEY": os.getenv("AWS_SECRET_ACCESS_KEY"),
        }

        self.lambdas = {
            # "InvokeLambdasFunction": DockerImageFunction(
            #     self,
            #     "ExpertiseToolsInvokeLambdasFunction",
            #     function_name="expertise-tools-invoke-lambdas",
            #     role=expertise_lambdas_role,
            #     timeout=Duration.minutes(15),
            #     memory_size=1024,
            #     code=DockerImageCode.from_image_asset(
            #         "invoke_lambdas/",
            #         build_args=build_arguments,
            #     ),
            # ),
            "InvokeECSTasksFunction": DockerImageFunction(
                self,
                "ExpertiseToolsInvokeECSTasksFunction",
                function_name="expertise-tools-invoke-ecs-tasks",
                role=expertise_lambdas_role,
                timeout=Duration.minutes(15),
                memory_size=1024,
                code=DockerImageCode.from_image_asset(
                    "invoke_ecs_tasks/",
                    build_args=build_arguments,
                ),
            ),
        }
