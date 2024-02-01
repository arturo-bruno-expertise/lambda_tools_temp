import json
from json import JSONDecodeError

from aws_lambda_powertools import Tracer
from aws_lambda_powertools.event_handler import APIGatewayRestResolver
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.utilities.typing import LambdaContext
from data_warehouse_common.google.campaigns import GoogleAdsCampaigns
from data_warehouse_common.utils import logger
from data_warehouse_common.aws import get_aws_session
from aws_lambda_powertools.event_handler.exceptions import BadRequestError

from pathlib import Path

tracer = Tracer()
google_ads_campaigns = GoogleAdsCampaigns()
app = APIGatewayRestResolver()
ecs_client = get_aws_session().client("ecs")

SUBNETS = ["subnet-ea11a181", "subnet-ed59b790", "subnet-3b762777"]

SECURITY_GROUPS = {
    "DataWarehouseSyncs": ["sg-09bd21ed2a8ee8fe7"],
    "DataWarehouseSalesforceSyncs": ["sg-0c9bf238505679c4d"],
}


def get_data(debug_params: dict = None):
    if debug_params:
        return debug_params

    try:
        data = app.current_event.json_body
    except TypeError:
        data = {}
    except JSONDecodeError:
        data = app.current_event.body

    if not data:
        params = app.current_event.query_string_parameters
        if not params:
            return {}

    return data


def execute_ecs_task(
    cluster_name: str,
    task_name: str,
    container_name: str,
    data: dict,
    started_by: str = None,
):
    try:
        env_vars = []
        network_security_groups = None

        for data_name, data_value in data.items():
            if isinstance(data_value, list):
                data_value = ",".join(data_value)
            env_vars.append({"name": data_name, "value": data_value})

        if security_groups := SECURITY_GROUPS.get(task_name):
            network_security_groups = security_groups

        if not network_security_groups:
            raise ValueError(
                f"No network security groups found for this task: '{task_name}'"
            )

        task_response = ecs_client.run_task(
            startedBy=f"Expertise tools - {started_by}",
            cluster=cluster_name,
            launchType="FARGATE",
            taskDefinition=f"{task_name}",
            count=1,
            networkConfiguration={
                "awsvpcConfiguration": {
                    "subnets": SUBNETS,
                    "assignPublicIp": "ENABLED",
                    "securityGroups": network_security_groups,
                }
            },
            overrides={
                "containerOverrides": [
                    {"name": container_name, "environment": env_vars}
                ]
            },
        )

        logger.info("Task response", extra={"response": task_response})

        return {"statusCode": 200, "body": task_response}
    except Exception as e:
        msg = "Could not create task"
        logger.error(msg, extra={"error": str(e)})
        return {"statusCode": 400, "body": msg}


@app.post("/tools/ecs_tasks/sync")
def tools_ecs_tasks_sync(params: dict = None):
    if params and "debug" in params:
        data = get_data(debug_params=params)
    else:
        data = get_data

    logger.info(f"Running manual sync", extra={"data": data})

    return execute_ecs_task(
        "DataWarehouseSyncsCluster",
        "DataWarehouseSyncs",
        "DataWarehouseSyncsContainer",
        data,
    )


@app.post("/tools/ecs_tasks/dw_to_sf_sync")
def tools_ecs_tasks_dw_to_sf_sync(params: dict = None):
    if params and "debug" in params:
        data = get_data(debug_params=params)
    else:
        data = get_data

    logger.info(
        f"Running manual Datawarehouse to Salesforce sync", extra={"data": data}
    )

    return execute_ecs_task(
        "DataWarehouseToSalesforceSyncsCluster",
        "DataWarehouseSalesforceSyncs",
        "DataWarehouseToSalesforceSyncsContainer",
        data,
        started_by=data.get("started_by"),
    )


@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_HTTP)
@tracer.capture_lambda_handler
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    logger.info("API call received", extra={"event": event})
    return app.resolve(event, context)


# This is only necessary if you are testing the Lambda function locally
if __name__ == "__main__":
    # event_data = {
    #     "table": "Provider",
    #     "force_update": "yes",
    #     "environment": "intermediate",
    #     "refresh_ids": ["4656900", "4656904", "4656901", "4656902", "4656903"],
    # }
    # lambda_result = tools_ecs_tasks_sync_job(event_data)

    event_data = {
        "debug": "True",
        "sync": "dim_provider",
        "started_by": "Arturo Bruno",
    }
    lambda_result = tools_ecs_tasks_dw_to_sf_sync(event_data)

    print(json.dumps(lambda_result, indent=4, default=str))
