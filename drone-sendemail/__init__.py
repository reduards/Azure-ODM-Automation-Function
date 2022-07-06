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

    payload={
        "status": inputPara,
    }
    
    url=keyvault_client.get_secret("logicapp-email").value

    send_message = requests.post(url, json=payload)
    
    logging.info(send_message)

    return inputPara
