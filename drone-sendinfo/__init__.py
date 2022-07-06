# This function is not intended to be invoked directly. Instead it will be
# triggered by an orchestrator function.
# Before running this sample, please:
# - create a Durable orchestration function
# - create a Durable HTTP starter function
# - add azure-functions-durable to requirements.txt
# - run pip install -r requirements.txt

import logging
import requests
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential
import os


def main(inputPara: str) -> str:
    key_vault = os.environ["vaultURI"]
    
    KVUri = key_vault
    credential = DefaultAzureCredential()
    keyvault_client = SecretClient(vault_url=KVUri, credential=credential)

    vm_size = inputPara["vmSize"]

    #calculate cost of vm size from cost api
    vm_size_split=vm_size.split('_')
    meterName=vm_size_split[1]+' '+vm_size_split[2]
    price_respones=requests.get("https://prices.azure.com/api/retail/prices?currencyCode='SEK'&$filter=meterName eq '"+meterName+"' and armRegionName eq 'westeurope' and priceType eq 'Consumption'")
    price_json=price_respones.json()
    first_item=(price_json['Items'][0])
    price_hour = first_item['unitPrice']
    price_seconds = price_hour/3600

    #varibles for alert message
    project_name = inputPara["projectName"]
    processing_time_seconds = float(inputPara["processingTimeSeconds"]) * 0.001
    date_created = inputPara["dateCreated"]
    cost = price_seconds * processing_time_seconds
    cost = str(round(cost, 2))
    image_count = inputPara["imagesCount"]
    job_options = inputPara["options"]
    status = "ODM Drone Job Completed Successfully!"

    payload={
        "status": status,
        "project_name": project_name,
        "processing_time_seconds": processing_time_seconds,
        "cost": cost + " Kr",
        "image_count": image_count,
        "job_options": job_options
    }

    url=keyvault_client.get_secret("logicapp-email").value

    send_message = requests.post(url, json=payload)
    
    logging.info(send_message)

    return "Sucessfully executed message alert!"

