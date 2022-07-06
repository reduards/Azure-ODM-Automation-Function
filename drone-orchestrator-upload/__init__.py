# This function is not intended to be invoked directly. Instead it will be
# triggered by an HTTP starter function.
# Before running this sample, please:
# - create a Durable activity function (default name is "Hello")
# - create a Durable HTTP starter function
# - add azure-functions-durable to requirements.txt
# - run pip install -r requirements.txt

import logging
import json

import azure.functions as func
import azure.durable_functions as df



def orchestrator_function(context: df.DurableOrchestrationContext):
    data = context.get_input()
    logging.info(data)
    try:
        #Validate parameter input
        result0 = yield context.call_activity('drone-validateinput', data)
        #If path exist, proceed
        if result0 == True:
            result1 = yield context.call_activity('drone-startcompute', data)
            if result1 == False:
                result4 = yield context.call_activity('drone-deletevm', data["randomUUID"])
                result5 = yield context.call_activity('drone-sendemail', "ERROR: VM Failed to launch")
                return result5
            result2 = yield context.call_activity('drone-upload', result1)
            #If drone upload failed delete VM
            if result2 ==False:
                result4 = yield context.call_activity('drone-deletevm', data["randomUUID"])
                result5 = yield context.call_activity('drone-sendemail', "ERROR: Job Failed on upload")
                return result5
            #Else return Job done
            else:
                return "Job Uploaded"
        #if path doesnt exist return invalid path
        else:
            logging.info("Invalid path")
            result6 = yield context.call_activity('drone-sendemail', "ERROR: Invalid path or no pictures in chosen path")
            return result6
    except Exception as e:
        logging.info(e)
        yield context.call_activity('drone-deletevm', data["randomUUID"])
        yield context.call_activity('drone-sendemail', "ERROR: Job Failed on upload")

main = df.Orchestrator.create(orchestrator_function)