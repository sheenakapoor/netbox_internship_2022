#!/usr/bin/env python3
# noqa E501
# pylint: disable= R0914, R0912, R0915, C0301
"""Script updates creation/ deletion/ modification of device/ vm/ interface."""

import os
import json
import yaml


def json2yaml(json_data, yaml_data):
    """Function updates YAML file when a device/vm/interface is modified/added/deleted."""
    if json_data["event"] == "updated":
        if json_data["model"] == "interface":
            # for interface, a mac address is modified
            device = json_data["data"]["device"]["name"]
            mac_address_old = json_data["snapshots"]["prechange"]["mac_address"]
            mac_address_new = json_data["snapshots"]["postchange"]["mac_address"]
            for i in yaml_data["psc_netconfig"][device]["interfaces"]:
                if i["hwaddr"] == mac_address_old:
                    interface = i
                    break
            interface["hwaddr"] = mac_address_new
        elif json_data["model"] == "vminterface":
            # for vminterface, a mac address is modified
            virtualmachine = json_data["data"]["virtual_machine"]["name"]
            mac_address_old = json_data["snapshots"]["prechange"]["mac_address"]
            mac_address_new = json_data["snapshots"]["postchange"]["mac_address"]
            for i in yaml_data["psc_netconfig"][virtualmachine]["interfaces"]:
                if i["hwaddr"] == mac_address_old:
                    vminterface = i
                    break
            vminterface["hwaddr"] = mac_address_new
        elif json_data["model"] == "device" or json_data["model"] == "virtualmachine":
            # for device/vm, name is changed
            device_vm_name_old = json_data["snapshots"]["prechange"]["name"]
            device_vm_name_new = json_data["snapshots"]["postchange"]["name"]
            yaml_data["psc_netconfig"][device_vm_name_new] = yaml_data["psc_netconfig"][device_vm_name_old]
            del yaml_data["psc_netconfig"][device_vm_name_old]

    if json_data["event"] == "created":
        if json_data["model"] == "interface":
            # interface is added; prechange will be null
            device = json_data["data"]["device"]["name"]
            # assuming when interface created, only hwaddr is added
            mac_address = json_data["snapshots"]["postchange"]["mac_address"]
            interface_list = {"hwaddr": mac_address, "ipaddr": None, "net": None, "netdev": None}
            yaml_data["psc_netconfig"][device]["interfaces"].append(interface_list)
        elif json_data["model"] == "vminterface":
            # vminterface is added; prechange will be null
            virtualmachine = json_data["data"]["virtual_machine"]["name"]
            # assuming when vminterface created, only hwaddr is added
            mac_address = json_data["snapshots"]["postchange"]["mac_address"]
            interface_list = {"hwaddr": mac_address, "ipaddr": None, "net": None, "netdev": None}
            yaml_data["psc_netconfig"][virtualmachine]["interfaces"].append(interface_list)
        elif json_data["model"] == "device" or json_data["model"] == "virtualmachine":
            # device/ vm is created; prechange will be null
            device_vm_name = json_data["snapshots"]["postchange"]["name"]
            # also add netbox_id in device. (if not none)
            yaml_data["psc_netconfig"][device_vm_name] = {'interfaces': []}

    if json_data["event"] == "deleted":
        if json_data["model"] == "interface":
            # interface is deleted; postchange will be null
            device = json_data["data"]["device"]["name"]
            # assuming when interface created, only hwaddr was present
            mac_address = json_data["snapshots"]["prechange"]["mac_address"]
            for i in yaml_data["psc_netconfig"][device]["interfaces"]:
                interface = None
                if i["hwaddr"] == mac_address:
                    interface = i
                    interface.clear()
                    yaml_data["psc_netconfig"][device]["interfaces"].remove({})
                    break
        elif json_data["model"] == "vminterface":
            # interface is deleted; postchange will be null
            virtualmachine = json_data["data"]["virtual_machine"]["name"]
            # assuming when interface created, only hwaddr was present
            mac_address = json_data["snapshots"]["prechange"]["mac_address"]
            for i in yaml_data["psc_netconfig"][virtualmachine]["interfaces"]:
                interface = None
                if i["hwaddr"] == mac_address:
                    interface = i
                    interface.clear()
                    yaml_data["psc_netconfig"][virtualmachine]["interfaces"].remove({})
                    break
        elif json_data["model"] == "device" or json_data["model"] == "virtualmachine":
            # device is deleted; postchange will be null
            device_name = json_data["snapshots"]["prechange"]["name"]
            device_entry = None
            for i in yaml_data["psc_netconfig"]:
                if i == device_name:
                    device_entry = i
                    yaml_data["psc_netconfig"].pop(device_entry)
                    break

    return yaml_data


if __name__ == "__main__":
    # Environment variable for JSON file
    nb_data_file = os.environ.get('NETBOX_PAYLOAD_FILE')
    if nb_data_file is None:
        # Setting environment variable manually
        temp_file = input("Enter name of temp file: ")
        nb_data_file = 'tmp/' + temp_file
    # Open files
    with open(nb_data_file, "r", encoding="utf8") as handle:
        json_parsed = json.load(handle)
    # Environment variable for YAML file
    input_file = os.environ.get('NETBOX_YAML_FILE')
    if input_file is None:
        # Setting environment variable manually
        input_file = input("Enter name of file to be edited: ")
    # Open files
    with open(input_file, encoding="utf8") as stream:
        try:
            yaml_parsed = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    # Make changes
    yaml_data = json2yaml(json_parsed, yaml_parsed)
    # Write in file, close
    with open(input_file, "w", encoding="utf8") as stream:
        yaml.explicit_end = True
        yaml.safe_dump(yaml_data, stream)
        print("The value has been updated!")
    stream.close()
