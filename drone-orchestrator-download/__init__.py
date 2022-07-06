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
        result1 = yield context.call_activity('drone-download', data)
        result2 = yield context.call_activity('drone-deletevm', data["vmID"])
        if result1 == False:
            result3 = yield context.call_activity('drone-sendemail', "Could not download job or there is no VM running")
        else:
            result3 = yield context.call_activity('drone-sendinfo', data)
        logging.info(result3)
        return result3
    #catch unexpected
    except:
        yield context.call_activity('drone-deletevm', data["vmID"])
        yield context.call_activity('drone-sendemail', "Could not download job or there is no VM running")
main = df.Orchestrator.create(orchestrator_function)