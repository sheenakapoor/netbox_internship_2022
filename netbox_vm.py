#!/usr/bin/env python
# pylint: disable=C0103, E0401, R0913, R1720, R0914
# noqa: E501
"""This script does something."""
import json
import pynetbox


# read json file for facts
with open("git_np_facts.json", "r", encoding="utf-8") as f:
    git_np_facts = json.load(f)


def netbox_connect(host, username=None, password=None, token=None):
    """Connect user to Netbox host."""
    if token is None and (username is None or password is None):
        raise Exception("Must provide netbox auth parameters")
    elif username is not None and password is not None:
        nb = pynetbox.api(host)
        token = nb.create_token(username, password)
    else:
        nb = pynetbox.api(host, token=token)
    return nb


def _create_interfaces(
    nb, input_type, input_name, input_mac, input_ip, virtual_machine
):
    """Create Interface with user inputs."""
    endpoint = nb.virtualization.interfaces
    # parent = virtual_machine
    endpoint_args = {"virtual_machine": virtual_machine.id}
    obj_type = "virtualization.vminterface"
    interfaces = []
    if input_type == "infiniband":
        i_type = "infiniband-hdr"
    elif input_type == "1gbe":
        i_type = "1000base-t"
    elif input_type == "10gbe":
        i_type = "10gbase-x-sfpp"
    i_name = input_name
    i_mac = input_mac
    i_ip = input_ip

    interface = endpoint.create(
        name=i_name, type=i_type, mac_address=i_mac, **endpoint_args
    )
    ip_options = {
        "address": i_ip,
        "assigned_object_type": obj_type,
        "assigned_object_id": interface.id,
    }
    nb.ipam.ip_addresses.create(**ip_options)
    interfaces.append(interface)
    return interfaces


def _create_vm(nb, facts, vm_cluster_id):
    """Create VM with user inputs."""
    created_vm = nb.virtualization.virtual_machines.create(
        name=facts["hostname"], cluster={"id": vm_cluster_id}
    )
    interfaces = _create_interfaces(
        netbox,
        interface_type,
        interface_name,
        mac_addr,
        ip_addr,
        virtual_machine=created_vm,
    )
    return (created_vm, interfaces)


if __name__ == "__main__":
    input_nbhost = input("Enter host address: ")
    input_username = input("Enter your Netbox username: ")
    input_password = input("Enter your Netbox password: ")
    netbox = netbox_connect(input_nbhost, input_username, input_password)

    cluster_id = input("Enter the Cluster ID: ")
    interface_name = input("Enter the Interface Name: ")
    interface_type = input(
        "Enter the Interface Type, choose from 'infiniband', '1gbe', '10gbe': "
    )
    mac_addr = input("Enter the MAC Address: ")
    ip_addr = input("Enter the IP Address: ")

    _create_vm(netbox, git_np_facts, cluster_id)
