# This function is not intended to be invoked directly. Instead it will be
# triggered by an orchestrator function.
# Before running this sample, please:
# - create a Durable orchestration function
# - create a Durable HTTP starter function
# - add azure-functions-durable to requirements.txt
# - run pip install -r requirements.txt

import logging
from os import path
import os
import glob
import os


def main(inputPara: str) -> str:
    file_share = os.environ["fileShare"]
    #Check if path exist
    path=f"/{file_share}/"+inputPara["projectName"]+"/"+inputPara["projectName"]+"_"+str(inputPara["projectDate"])
    logging.info(path)
    result0=os.path.isdir(path)
    #Check if path contains images
    if result0==True:
        my_files=glob.glob(path+"/*.JPG")
        my_files=my_files+glob.glob(path+"/*.jpg")
        if my_files == []:
            result0=False
            
    return result0
