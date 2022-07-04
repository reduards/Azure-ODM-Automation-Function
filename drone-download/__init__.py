# This function is not intended to be invoked directly. Instead it will be
# triggered by an orchestrator function.
# Before running this sample, please:
# - create a Durable orchestration function
# - create a Durable HTTP starter function
# - add azure-functions-durable to requirements.txt
# - run pip install -r requirements.txt

import logging
import os
from pyodm import Node, exceptions

def main(name: str) -> str:
    try:
        file_share = os.environ["fileShare"]
        logging.info('Python HTTP trigger function processed a request.')

        #Bind values from incoming post request
        true_uuid = name[0]
        ip_adress = name[1]
        project_name = name[2]

        #ODM computing node
        node = Node(ip_adress, 3000)

        #Bind task with job id
        task = node.get_task(true_uuid)
        logging.info(task.info())

        #Download result as zip
        zip_dir = f"/{file_share}/"+project_name+"/result/"
        task.download_zip(zip_dir)

        return project_name
    except exceptions as e:
        return False