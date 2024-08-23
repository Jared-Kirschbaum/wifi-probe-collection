# Wi-Fi Probe Request Capturer

This Python script captures Wi-Fi probe request packets using the `scapy` library, extracts relevant information such as the MAC address and SSID, and sends this data to an Azure IoT Hub. The script is designed to run on an interface (e.g., "panda") capable of monitoring Wi-Fi traffic.

## Prerequisites

Before running the script, ensure you have the following installed:

- Python 3.6+
- `scapy` library
- `azure-iot-device` library
- `python-dotenv` library

You can install the required Python packages using:

```bash
pip install scapy azure-iot-device python-dotenv
```

## Environment Setup

Create a `.env` file in the same directory as the script with the following content:

```plaintext
IOT_HUB_CONNECTION_STRING=<your_azure_iot_hub_connection_string>
```

Replace `<your_azure_iot_hub_connection_string>` with your actual Azure IoT Hub connection string.

## Script Overview

### Functionality

- **Probe Request Detection**: The script detects Wi-Fi probe request packets by inspecting captured packets for the `Dot11ProbeReq` layer.
  
- **Random MAC Address Detection**: The script checks if the MAC address is randomized based on the second character of the MAC address.

- **Data Payload Creation**: The script generates a JSON payload containing the MAC address, SSID, and whether the MAC address is randomized.

- **IoT Hub Integration**: Captured probe request data is sent to Azure IoT Hub as a message.

### Main Components

- **`has_probe_request(packet) -> bool`**: Checks if a packet is a probe request.
- **`is_random_mac(mac_address: str) -> int`**: Determines if the MAC address is randomized.
- **`create_payload(mac_address: str, ssid: str) -> str`**: Creates a JSON payload from the MAC address and SSID.
- **`packet_handler(packet) -> None`**: Processes each captured packet and sends the information to Azure IoT Hub.

### Packet Capture

The script captures packets on the specified network interface ("panda" in this example) and filters for 802.11 management frames, specifically probe requests:

```python
sniff(iface="panda", prn=packet_handler, filter="wlan type mgt subtype probe-req")
```

## Running the Script

To run the script:

1. Ensure your environment is set up correctly and the necessary Python packages are installed.
2. Set your Azure IoT Hub connection string in the `.env` file.
3. Execute the script:

```bash
python wifi_probe_request_capturer.py
```

The script will start capturing Wi-Fi probe request packets on the specified interface and send the data to Azure IoT Hub.

## Notes

- The script requires a network interface capable of monitoring mode to capture Wi-Fi traffic.
- Ensure you have the necessary permissions to capture Wi-Fi traffic on your system.
- The MAC address randomization detection is based on the second hexadecimal character of the MAC address.

## License

This project is licensed under the MIT License.
```
