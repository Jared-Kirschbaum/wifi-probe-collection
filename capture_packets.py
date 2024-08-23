from scapy.all import sniff, Dot11ProbeReq
import json
from azure.iot.device import IoTHubDeviceClient, Message
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
    return 1 if mac_address[1] in {"2", "6", "A", "E"} else 0

def create_payload(mac_address: str, ssid: str) -> str:
    """Create a JSON payload from the MAC address and SSID."""
    event_data = {
        "mac_address": mac_address,
        "ssid": ssid,
        "random_mac": is_random_mac(mac_address)
    }
    return json.dumps(event_data)

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

# Start capturing packets on the "panda" interface, filtering for probe request frames
sniff(iface="panda", prn=packet_handler, filter="wlan type mgt subtype probe-req")
