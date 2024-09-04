import os
import uuid
import base64
from dotenv import load_dotenv
from azure.iot.hub import IoTHubRegistryManager
from azure.iot.device import IoTHubDeviceClient

# Load environment variables from .env file
load_dotenv()

# Retrieve the IoT Hub connection string from the environment
CONNECTION_STRING = os.getenv("IOT_HUB_CONNECTION_STRING")

# Parse HostName from the connection string
def extract_host_name(connection_string: str) -> str:
    try:
        # Split the connection string and find the part with HostName
        parts = connection_string.split(';')
        for part in parts:
            if part.startswith("HostName"):
                return part.split('=')[1]
        raise ValueError("HostName not found in connection string")
    except Exception as e:
        print(f"Failed to extract HostName: {e}")
        return None

# Extract the HostName
IOT_HUB_HOST_NAME = extract_host_name(CONNECTION_STRING)

# Function to generate a base64-encoded key
def generate_base64_key() -> str:
    try:
        return base64.b64encode(os.urandom(32)).decode('utf-8')
    except Exception as e:
        print(f"Failed to Generate Keys: {e}")

def generate_device_id() -> str:
    try:
        return f"device-{uuid.uuid4()}"
    except Exception as e:
        print(f"Failed to Generate Device ID: {e}")

def create_iot_hub_connection():
    return IoTHubRegistryManager(CONNECTION_STRING)

def read_env_file() -> dict:
    """Read the .env file and return a dictionary of the existing keys and values."""
    env_vars = {}
    try:
        with open('.env', 'r') as env_file:
            for line in env_file:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    env_vars[key] = value
    except FileNotFoundError:
        print(".env file not found, it will be created.")
    return env_vars

def update_env_file(device_id: str, primary_key: str, secondary_key: str, connection_string: str) -> None:
    env_vars = read_env_file()
    
    # Check if keys already exist in the .env file, and add them with quotes if they don't
    if 'DEVICE_ID' in env_vars:
        print(f"DEVICE_ID is already set: {env_vars['DEVICE_ID']}. Skipping.")
    else:
        with open('.env', 'a') as env_file:
            env_file.write(f'\nDEVICE_ID="{device_id}"')
    
    if 'PRIMARY_KEY' in env_vars:
        print(f"PRIMARY_KEY is already set: {env_vars['PRIMARY_KEY']}. Skipping.")
    else:
        with open('.env', 'a') as env_file:
            env_file.write(f'\nPRIMARY_KEY="{primary_key}"')
    
    if 'SECONDARY_KEY' in env_vars:
        print(f"SECONDARY_KEY is already set: {env_vars['SECONDARY_KEY']}. Skipping.")
    else:
        with open('.env', 'a') as env_file:
            env_file.write(f'\nSECONDARY_KEY="{secondary_key}"')
    
    if 'DEVICE_CONNECTION_STRING' in env_vars:
        print(f"DEVICE_CONNECTION_STRING is already set: {env_vars['DEVICE_CONNECTION_STRING']}. Skipping.")
    else:
        with open('.env', 'a') as env_file:
            env_file.write(f'\nDEVICE_CONNECTION_STRING="{connection_string}"')
    
    print(f".env file updated with new device info if not already set.")

def remove_iot_hub_connection_string() -> None:
    """Remove the IOT_HUB_CONNECTION_STRING from the .env file."""
    try:
        with open('.env', 'r') as env_file:
            lines = env_file.readlines()
        
        # Re-open the file in write mode and write all lines except the one containing IOT_HUB_CONNECTION_STRING
        with open('.env', 'w') as env_file:
            for line in lines:
                if not line.startswith("IOT_HUB_CONNECTION_STRING"):
                    env_file.write(line)
        
        print("IOT_HUB_CONNECTION_STRING removed from .env file.")
    
    except Exception as e:
        print(f"Failed to remove IOT_HUB_CONNECTION_STRING: {e}")

def register_device() -> None:
    try:
        registry_manager = create_iot_hub_connection()
    except Exception as e:
        print(f"Failed to connect to IoT Hub: {e}")
        return

    try:
        device_id = generate_device_id()
        primary_key = generate_base64_key()
        secondary_key = generate_base64_key()
        
        # Register the device with the IoT Hub
        registry_manager.create_device_with_sas(
            device_id=device_id,
            primary_key=primary_key,
            secondary_key=secondary_key,
            status="enabled"
        )

        print(f"Created device: {device_id}")

        # Generate the device connection string
        device_connection_string = f"HostName={IOT_HUB_HOST_NAME};DeviceId={device_id};SharedAccessKey={primary_key}"

        # Update .env file with the new device info
        update_env_file(device_id, primary_key, secondary_key, device_connection_string)

        # Remove IOT_HUB_CONNECTION_STRING from the .env file
        remove_iot_hub_connection_string()

    except Exception as ex:
        if "DeviceAlreadyExists" in str(ex):
            print(f"Device '{device_id}' already exists. Skipping.")
        else:
            print(f"Failed to create device '{device_id}': {ex}")

def is_device_already_registered() -> bool:
    """Check if the necessary values for device registration are already set in the .env file."""
    env_vars = read_env_file()
    return all(key in env_vars for key in ['DEVICE_ID', 'PRIMARY_KEY', 'SECONDARY_KEY', 'DEVICE_CONNECTION_STRING'])

if __name__ == "__main__":
    if not is_device_already_registered():
        print("Device not registered. Registering now...")
        register_device()
    else:
        DEVICE_ID = os.getenv("DEVICE_ID")
        print(f"Device already registered: {DEVICE_ID}")

    try:
        load_dotenv()
    except Exception as e:
        print(f"Failed to load .env file: {e}")


    # After device is registered, create the IoTHubDeviceClient with the device-specific connection string
    DEVICE_CONNECTION_STRING = os.getenv("DEVICE_CONNECTION_STRING")
    if DEVICE_CONNECTION_STRING:
        client = IoTHubDeviceClient.create_from_connection_string(DEVICE_CONNECTION_STRING)
        print("IoT Hub client created successfully.")
    else:
        print("Device connection string not found in .env file.")
