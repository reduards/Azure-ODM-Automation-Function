# This function is not intended to be invoked directly. Instead it will be
# triggered by an orchestrator function.
# Before running this sample, please:
# - create a Durable orchestration function
# - create a Durable HTTP starter function
# - add azure-functions-durable to requirements.txt
# - run pip install -r requirements.txt

import logging
from pyodm import Node, exceptions
import sys,os
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential
import glob
import os


def main(name: str) -> str:
    try:
        logging.info('Python HTTP trigger function processed a request.')

        logging.info("Node ip "+ name[0])

        azure_function_name = os.environ["azureFunctionName"]
        file_share = os.environ["fileShare"]

        ipadress=name[0]
        job_name=name[1]
        VM_SIZE=name[2]
        job_date=name[3]
        job_option=name[4]
        random_uuid=name[5]

        #Keyvault connection
        KVUri = os.environ["vaultURI"]
        credential = DefaultAzureCredential()
        keyvault_client = SecretClient(vault_url=KVUri, credential=credential)
        functionkey=keyvault_client.get_secret("functionkey").value

        #ODM compute node
        node = Node(ipadress, 3000)

        #Set up webhook with job id which is sent when job is done
        webhook = f"https://{azure_function_name}.azurewebsites.net/api/orchestrators/drone-orchestrator-download" + "?code=" + functionkey + "&ipAdress=" + ipadress + "&vmSize=" + VM_SIZE + "&vmID=" + random_uuid

        #Create list from images residing in file share

        path = f"/{file_share}/"+job_name+"/"+job_name+"_"+job_date
        my_files=glob.glob(path+"/*.JPG")
        my_files=my_files+glob.glob(path+"/*.jpg")

        #Define options depending on input
        if job_option=="1":
            options={'camera-lens':'brown','dem-resolution': 4.0,'depthmap-resolution':1024,'fast-orthophoto' : True, 'orthophoto-resolution': 1,'tiles': True,}
        elif job_option=="2":
            options={'dsm': True, 'orthophoto-resolution': 2}
        else:
            options={'dsm': True, 'fast-orthophoto' : True, 'orthophoto-resolution': 2}

        #Create task on the worker node by specifying parameters. Pictures, resolution, webhook name etc
        logging.info("Uploading images...")
        task = node.create_task(my_files,
                                options, job_name+"-"+job_date, None, False, webhook)

        #Task info and aquire job uuuid
        logging.info("Task is being processed at: "+ipadress)
        logging.info(task.info())
        return "Sucessfully uploaded images!"

    except exceptions.NodeConnectionError as e:
        logging.info("Cannot connect: %s" % e)
        return [False, random_uuid]
    except exceptions.NodeResponseError as e:
        logging.info("Error: %s" % e)
        return [False, random_uuid]
    except exceptions as e:
        return [False, random_uuid]
