#!/usr/bin/env python3
import subprocess
import re
import argparse
import platform

def get_args():
    parser = argparse.ArgumentParser(description="Change MAC address of a network interface.")
    parser.add_argument("-i", "--interface", dest="interface", required=True,
                        help="Interface to change its MAC address")
    parser.add_argument("-m", "--mac", dest="new_mac", required=True,
                        help="New MAC address")
    args = parser.parse_args()
    return args

def valid_mac(mac):
    return re.match(r"^[0-9a-fA-F]{2}(:[0-9a-fA-F]{2}){5}$", mac) is not None

def change_mac(interface, new_mac):
    os_type = platform.system().lower()

    try:
        if os_type == "windows":
            subprocess.run(["netsh", "interface", "set", "interface", interface, "admin=disable"], check=True)
            subprocess.run(["netsh", "interface", "set", "interface", interface, "mac=" + new_mac], check=True)
            subprocess.run(["netsh", "interface", "set", "interface", interface, "admin=enable"], check=True)
        elif os_type in ["linux", "darwin"]:  # 'darwin' is for macOS
            subprocess.run(["sudo", "ifconfig", interface, "down"], check=True)
            subprocess.run(["sudo", "ifconfig", interface, "hw", "ether", new_mac], check=True)
            subprocess.run(["sudo", "ifconfig", interface, "up"], check=True)
        else:
            print(f"Unsupported OS: {os_type}")
            return
    except subprocess.CalledProcessError as e:
        print(f"Failed to change MAC address: {e}")

def get_current_mac(interface):
    os_type = platform.system().lower()

    try:
        if os_type == "windows":
            output = subprocess.check_output(["getmac", "/fo", "csv", "/v"], shell=True).decode("utf-8")
            interface_data = [line for line in output.splitlines() if interface in line]
            if interface_data:
                mac_address_search = re.search(r'([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})', interface_data[0])
                if mac_address_search:
                    return mac_address_search.group(0)
        elif os_type in ["linux", "darwin"]:
            output = subprocess.check_output(["ifconfig", interface]).decode("utf-8")
            mac_address_search = re.search(r"(\w\w:\w\w:\w\w:\w\w:\w\w:\w\w)", output)
            if mac_address_search:
                return mac_address_search.group(0)
        else:
            print(f"Unsupported OS: {os_type}")
            return None

        print("Could not read MAC address.")
        return None
    except subprocess.CalledProcessError as e:
        print(f"Failed to get MAC address: {e}")
        return None

def main():
    interface = input("Enter the name of the Interface (e.g., eth0, wlan0, Wi-Fi): ")
    new_mac = input("Enter the new MAC address (e.g., 00:11:22:33:44:55): ")

    if not valid_mac(new_mac):
        print("Invalid MAC format.")
        return

    current_mac = get_current_mac(interface)
    if current_mac:
        print(f"Current MAC address: {current_mac}")
    else:
        return

    change_mac(interface, new_mac)

    current_mac = get_current_mac(interface)
    if current_mac == new_mac:
        print(f"MAC address was successfully changed to {current_mac}")
    else:
        print("MAC address did not get changed.")

if __name__ == "__main__":
    main()
