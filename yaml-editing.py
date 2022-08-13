#!/usr/bin/env python
# pylint: disable=C0103, E0401, W0107, R0913, R1705
# noqa: E501
"""This script replaces value of one key based on user input."""
import sys
import re
import ipaddress
import yaml


class NetboxInputError(Exception):
    """Class indicating invalid user inputs."""

    pass


class YamlEditor:
    """
    Class containing functions to do the following tasks:
    1. Open YAML file and read the data
    2. Take inputs from user and check for their validity
    3. Replace the value in the desired location in the dictionary
    4. Save changes in a file called output.yaml

    Attributes:
    filename = Name of file to be edited
    device: Name of device
    netdev: Name of netdev (ens10f0, ib0, ens10f1, ens3f0)
    iface_key: Name of interface key (hwaddr, ipaddr, net, netdev)
    value: Key value for certain device interface
    """

    def __init__(self, filename, device, netdev, iface_key, value):
        self.filename = filename
        # Read yaml file
        """Open the YAML file and read data."""
        with open(filename, encoding="utf8") as stream:
            try:
                self.data = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)
        self.device = device
        self.netdev = netdev
        self.iface_key = iface_key
        self.value = value

    @classmethod
    def get_user_input(cls):
        """Take user input."""
        filename = input("Enter File Name (with extension): ")
        device = input("Enter device: ")
        netdev = input("Enter netdev: ")
        iface_key = input("Enter key: ")
        value = input("Enter new value: ")
        return cls(filename, device, netdev, iface_key, value)

    # Checking for validity of user inputs
    @staticmethod
    def check_inputs(error_message, keys, value):
        """Check device name, netdev name, iface_key with this function."""
        if value in keys:
            return True
        else:
            raise NetboxInputError(error_message)

    @staticmethod
    def validate_ip_address(error_message, address):
        """Check IP address validity."""
        try:
            ipaddress.ip_address(address)
        except ValueError:
            print(NetboxInputError(error_message))
            sys.exit()

    @staticmethod
    def validate_mac_address(error_message, address):
        """Check MAC address validity."""
        is_valid_mac = re.match(
            "^([0-9A-Fa-f]{2}[:-])"
            + "{5}([0-9A-Fa-f]{2})|"
            + "([0-9a-fA-F]{4}\\."
            + "[0-9a-fA-F]{4}\\."
            + "[0-9a-fA-F]{4})$",
            string=address,
            flags=re.IGNORECASE,
        )
        if is_valid_mac is not None:
            return True
        else:
            raise NetboxInputError(error_message)

    def replace(self):
        """Make changes in the YAML file based on the user inputs."""
        # Validating inputs
        device_names = self.data["psc_netconfig"].keys()
        self.check_inputs(
            f"Device Name {self.device} isn't valid", device_names, self.device
        )
        interface = None
        for i in self.data["psc_netconfig"][self.device]["interfaces"]:
            if i["netdev"] == self.netdev:
                interface = i
                break
        if interface is None:
            raise NetboxInputError(f"NetDev Name {self.netdev} is not valid")
        iface_names = interface.keys()
        self.check_inputs(
            f"Interface Key Name {self.iface_key} is not valid",
            iface_names,
            self.iface_key,
        )
        if self.iface_key == "ipaddr":
            self.validate_ip_address(
                f"IP address {self.value} is not valid", self.value
            )
        elif self.iface_key == "hwaddr":
            self.validate_mac_address(
                f"MAC address {self.value} is not valid", self.value
            )

        # Replace existing value with user input value
        interface[self.iface_key] = self.value
        return interface

    # Write in file, close
    def generate_output(self):
        """Save the changes in output.yaml file."""
        with open("output.yaml", "w", encoding="utf8") as stream:
            yaml.safe_dump(self.data, stream)
            print("The value has been updated!")
            yaml.explicit_end = True
        stream.close()


def main():
    """Executes all functions to make changes in the YAML file."""
    # Inputs
    edtr = YamlEditor.get_user_input()
    # Replace key value
    edtr.replace()
    # Output
    edtr.generate_output()


if __name__ == "__main__":
    main()
