# This function an HTTP starter function for Durable Functions.
# Before running this sample, please:
# - create a Durable orchestration function
# - create a Durable activity function (default name is "Hello")
# - add azure-functions-durable to requirements.txt
# - run pip install -r requirements.txt
 
from datetime import date
import logging

import azure.functions as func
import azure.durable_functions as df
import random
import string


async def main(req: func.HttpRequest, starter: str) -> func.HttpResponse:
    client = df.DurableOrchestrationClient(starter)
    if req.route_params["functionName"]=="drone-orchestrator-download":
        req_body = req.get_json()
        dataDict = {
            "uuid": req_body.get("uuid"),
            "projectName": req_body.get("name"),
            "processingTimeSeconds": req_body.get("processingTime"),
            "imagesCount": req_body.get("imagesCount"),
            "ipAddress": req.params.get("ipAddress"),
            "status": req_body.get("status"),
            "progress": req_body.get("progress"),
            "options": req_body.get("options"),
            "vmSize": req.params.get("vmSize"),
            "vmID": req.params.get("vmID"),
            "dateCreated": req_body.get("dataCreated")
        }

        instance_id = await client.start_new(req.route_params["functionName"], None, dataDict)
        logging.info(f"Started orchestration with ID = '{instance_id}'.")
        return "Successfully invoked download and delte action!"
    else:
        random_uuid=''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])

        dataDict = {
            "projectName": req.params.get("projectName"),
            "vmSize": req.params.get("vmSize"),
            "jobOption": req.params.get("jobOption"),
            "randomUUID": random_uuid,
            "projectDate": req.params.get("projectDate")
        }
    
        instance_id = await client.start_new(req.route_params["functionName"], None, dataDict)
        logging.info(f"Started orchestration with ID = '{instance_id}'.")
        return client.create_check_status_response(req, instance_id)