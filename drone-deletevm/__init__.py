# This function is not intended to be invoked directly. Instead it will be
# triggered by an orchestrator function.
# Before running this sample, please:
# - create a Durable orchestration function
# - create a Durable HTTP starter function
# - add azure-functions-durable to requirements.txt
# - run pip install -r requirements.txt

import logging
from azure.identity import DefaultAzureCredential
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.resource import SubscriptionClient
from pyodm import exceptions
import os

def main(inputPara: str) -> str:
    try:

        resource_group = os.environ["resourceGroup"]
        # Acquire a credential object using CLI-based authentication.
        credential = DefaultAzureCredential()

        # Retrieve subscription ID from environment variable.
        subscription_client = SubscriptionClient(credential)
        subscription = next(subscription_client.subscriptions.list())
        subscription_id = subscription.subscription_id

        #conenction for network and compute
        compute_client = ComputeManagementClient(credential, subscription_id)
        network_client = NetworkManagementClient(credential, subscription_id)

        #VM variables
        nic_name = "node-nic-"+ inputPara
        vm_name = "node-compute-"+ inputPara
        group_name = resource_group
        ip_name="node-ip-"+ inputPara
        disk_name= "node-disk-" + inputPara

        # Delete VM
        logging.info('Deleting VM {}'.format(vm_name)+'...')

        async_vm_delete = compute_client.virtual_machines.begin_delete(group_name, vm_name)
        async_vm_delete.wait()
        net_del_poller = network_client.network_interfaces.begin_delete(group_name, nic_name)
        net_del_poller.wait()
        async_disk_delete = compute_client.disks.begin_delete(group_name, disk_name)
        async_disk_delete.wait()
        ip_del_poller = network_client.public_ip_addresses.begin_delete(group_name, ip_name)
        ip_del_poller.wait()
        
        
        done_message="Deleted VM {}".format(vm_name)+" and all belonging components"
        logging.info(done_message)

        return done_message
    except exceptions as e:
        return False