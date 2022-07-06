# This function is not intended to be invoked directly. Instead it will be
# triggered by an orchestrator function.
# Before running this sample, please:
# - create a Durable orchestration function
# - create a Durable HTTP starter function
# - add azure-functions-durable to requirements.txt
# - run pip install -r requirements.txt

import logging
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.compute import ComputeManagementClient
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import SubscriptionClient
import os

def main(inputPara: str) -> str:
    try:
        random_uuid=inputPara["randomUUID"]
        VM_SIZE=inputPara["vmSize"]

        #Keyvault connection
        KVUri = os.environ["vaultURI"]
        credential = DefaultAzureCredential()
        keyvault_client = SecretClient(vault_url=KVUri, credential=credential)

        # Retrieve subscription ID from environment variable.
        subscription_client = SubscriptionClient(credential)
        subscription = next(subscription_client.subscriptions.list())
        subscription_id = subscription.subscription_id

        logging.info(f"Provisioning a virtual machine...some operations might take a minute or two.")

        # Acquire a credential object using CLI-based authentication.
        #credential = AzureCliCredential()

        # Step 1: Provision a resource group

        # Obtain the management object for resources, using the credentials from the CLI login.
        resource_client = ResourceManagementClient(credential, subscription_id)

        # Obtain the management object for networks
        network_client = NetworkManagementClient(credential, subscription_id)

        # Obtain the management object for virtual machines
        compute_client = ComputeManagementClient(credential, subscription_id)

        # Constants we need in multiple places: the resource group name and the region
        # in which we provision resources. You can change these values however you want.
        RESOURCE_GROUP_NAME = os.environ["resourceGroup"]
        LOCATION = os.environ["location"]

        # Network and IP address names
        VNET_NAME = os.environ["networkVNET"]
        SUBNET_NAME = os.environ["networkSubnet"]
        IP_NAME = "node-ip-" + random_uuid
        IP_CONFIG_NAME = "node-ip-config-" + random_uuid
        NIC_NAME = "node-nic-" + random_uuid
        DISK_NAME = "node-disk-" + random_uuid

        #Compute information
        VM_NAME = "node-compute-"+random_uuid
        USERNAME = "azureuser"
        PASSWORD = keyvault_client.get_secret("localadminpassword").value

        #To create resource group, VNET and subnet remove comment mark """ """
        """
        # Provision the resource group.
        rg_result = resource_client.resource_groups.create_or_update(RESOURCE_GROUP_NAME,
            {
                "location": LOCATION
            }
        )

        logging.info(f"Provisioned resource group {rg_result.name} in the {rg_result.location} region")

        # For details on the previous code, see Example: Provision a resource group
        # at https://docs.microsoft.com/azure/developer/python/azure-sdk-example-resource-group


        # Step 2: provision a virtual network

        # A virtual machine requires a network interface client (NIC). A NIC requires
        # a virtual network and subnet along with an IP address. Therefore we must provision
        # these downstream components first, then provision the NIC, after which we
        # can provision the VM.

        # Provision the virtual network and wait for completion
        poller = network_client.virtual_networks.begin_create_or_update(RESOURCE_GROUP_NAME,
            VNET_NAME,
            {
                "location": LOCATION,
                "address_space": {
                    "address_prefixes": ["10.0.0.0/16"]
                }
            }
        )

        vnet_result = poller.result()

        logging.info(f"Provisioned virtual network {vnet_result.name} with address prefixes {vnet_result.address_space.address_prefixes}")

        # Step 3: Provision the subnet and wait for completion
        poller = network_client.subnets.begin_create_or_update(RESOURCE_GROUP_NAME, 
            VNET_NAME, SUBNET_NAME,
            { "address_prefix": "10.0.0.0/24" }
        )
        subnet_result = poller.result()

        logging.info(f"Provisioned virtual subnet {subnet_result.name} with address prefix {subnet_result.address_prefix}")
        """

        # Step 4: Provision an IP address and wait for completion
        poller = network_client.public_ip_addresses.begin_create_or_update(RESOURCE_GROUP_NAME,
            IP_NAME,
            {
                "location": LOCATION,
                "sku": { "name": "Standard" },
                "public_ip_allocation_method": "Static",
                "public_ip_address_version" : "IPV4"
            }
        )

        ip_address_result = poller.result()


        logging.info(f"Provisioned public IP address {ip_address_result.name} with address {ip_address_result.ip_address}")

        # Step 5: Provision the network interface client
        poller = network_client.network_interfaces.begin_create_or_update(RESOURCE_GROUP_NAME,
            NIC_NAME, 
            {
                "location": LOCATION,
                "ip_configurations": [ {
                    "name": IP_CONFIG_NAME,
                    "subnet": { "id": f"/subscriptions/{subscription_id}/resourceGroups/{RESOURCE_GROUP_NAME}/providers/Microsoft.Network/virtualNetworks/{VNET_NAME}/subnets/{SUBNET_NAME}" },
                    "public_ip_address": {"id": ip_address_result.id }
                }]
            }
        )

        nic_result = poller.result()

        logging.info(f"Provisioned network interface client {nic_result.name}")

        """
        #Get private ip
        nic_client=network_client.network_interface_ip_configurations.get(RESOURCE_GROUP_NAME, NIC_NAME, IP_CONFIG_NAME)

        private_ip=nic_client.private_ip_address

        logging.info(f"Provisioned network interface with private ip {private_ip}")

        """

        # Step 6: Provision the virtual machine

        logging.info(f"Provisioning virtual machine {VM_NAME}; this operation might take a few minutes.")

        # Provision the VM specifying only minimal arguments, which defaults to an Ubuntu 18.04 VM
        # on a Standard DS1 v2 plan with a public IP address and a default virtual network/subnet.

        poller = compute_client.virtual_machines.begin_create_or_update(RESOURCE_GROUP_NAME, VM_NAME,
            {
                "location": LOCATION,
                "plan": {
                    "name": "ngc-base-version-21-11-0",
                    "publisher": "nvidia",
                    "product": "ngc_azure_17_11"
                },
                "storage_profile": {
                    "image_reference": {
                        "publisher": 'nvidia',
                        "offer": "ngc_azure_17_11",
                        "sku": "ngc-base-version-21-11-0",
                        "version": "latest"
                    },
                    'os_disk': {
                        'caching': 'ReadWrite',
                        'name' : DISK_NAME,
                        'create_option': 'FromImage',
                        'disk_size_gb': 1000,
                        'os_type': 'Linux',
                        'managed_disk': {
                            'storage_account_type': 'Premium_LRS'
                        }                        
                    }
                },
                "hardware_profile": {
                    "vm_size": VM_SIZE
                },
                "os_profile": {
                    "computer_name": VM_NAME,
                    "admin_username": USERNAME,
                    "admin_password": PASSWORD
                },
                "network_profile": {
                    "network_interfaces": [{
                        "id": nic_result.id,
                    }]
                }        
            }
        )

        vm_result = poller.result()

        logging.info(f"Provisioned virtual machine {vm_result.name}")

        logging.info("Spinning up the docker image")

        run_command_parameters = {
            'command_id': 'RunShellScript', # For linux, don't change it
            'script': ['docker run -d -p 3000:3000 --gpus all opendronemap/nodeodm:gpu'
            ]
        }
        poller = compute_client.virtual_machines.begin_run_command(
            RESOURCE_GROUP_NAME,
            vm_result.name,
            run_command_parameters
        )

        result = poller.result()  # Blocking till executed
        logging.info(result.value[0].message)  # stdout/stderr

        inputPara["ipAddress"]=ip_address_result.ip_address

        return inputPara
    except Exception as e:
        return False