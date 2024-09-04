import sys
from scapy.all import sniff, Dot11ProbeReq
import json
from azure.iot.device import IoTHubDeviceClient, Message
from azure.iot.hub import IoTHubRegistryManager
import os
import uuid
import base64
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Retrieve the IoT Hub connection string from the environment
CONNECTION_STRING = os.getenv("IOT_HUB_CONNECTION_STRING")

# Create an IoT Hub client
client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)


def has_probe_request(packet) -> bool:
    """Check if the packet is a probe request."""
    return packet.haslayer(Dot11ProbeReq) and packet.info

def is_random_mac(mac_address: str) -> int:
    """Determine if the MAC address is randomized."""
    return 1 if mac_address[1].upper() in {"2", "6", "A", "E"} else 0

def create_payload(mac_address: str, ssid: str) -> str:
    """Create a JSON payload from the MAC address and SSID."""
    event_data = {
        "mac_address": mac_address,
        "ssid": ssid,
        "random_mac": is_random_mac(mac_address)
    }
    return json.dumps(event_data)

# Function to generate a base64-encoded key
def generate_base64_key() -> str:
    
    try:        
        return base64.b64encode(os.urandom(32)).decode('utf-8')
    
    except Exception as e:
        print(f"Failed to Generate Keys: {e}")

def generate_device_id() -> str:

    try:
        return f"BOWSER-{uuid.uuid4()}"

    except Exception as e:
        print(f"Failed to Generate Device ID: {e}")

def create_iot_hub_connection():

    return IoTHubRegistryManager(CONNECTION_STRING)


def register_device(device_id: str) -> None:
    

    try:

        registry_manager = create_iot_hub_connection()

    except Exception as e:

        print(f"Failed to connect to IOT Hub: {e}")


    try:

        device_id = f"DEVICE-{uuid.uuid4()}"

        registry_manager.create_device_with_sas(
        device_id=generate_device_id,
        primary_key=generate_base64_key(),
        secondary_key=generate_base64_key(),
        status="enabled"
        )
        
        print(f"Created device: {device_id}")

    except Exception as ex:
        
        if "DeviceAlreadyExists" in str(ex):
            print(f"Device '{device_id}' already exists. Skipping.")
        else:
            print(f"Failed to create device '{device_id}': {ex}")

def packet_handler(packet) -> None:
    """Handle each captured packet."""
    if has_probe_request(packet):
        mac_address = packet.addr2
        ssid = packet.info.decode()

        message = create_payload(mac_address, ssid)

        try:
            print(f"Sending message: {message}")
            client.send_message(Message(message))
            print("Sent probe request event to IoT Hub")
        except Exception as e:
            print(f"Failed to send message: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script_name.py <interface>")
        sys.exit(1)

    interface = sys.argv[1]

    # Start capturing packets on the specified interface, filtering for probe request frames
    sniff(iface=interface, prn=packet_handler, filter="wlan type mgt subtype probe-req")
