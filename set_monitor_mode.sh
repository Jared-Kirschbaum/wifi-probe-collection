#!/bin/bash

# Check if an interface name was provided
if [ -z "$1" ]; then
    echo "Usage: $0 <interface_name>"
    exit 1
fi

INTERFACE=$1

# Bring the interface down
echo "Bringing down the interface $INTERFACE..."
sudo ip link set $INTERFACE down

# Set the interface to monitor mode
echo "Setting the interface $INTERFACE to monitor mode..."
sudo iwconfig $INTERFACE mode monitor

# Bring the interface back up
echo "Bringing up the interface $INTERFACE..."
sudo ip link set $INTERFACE up

# Verify the mode
echo "Verifying that $INTERFACE is in monitor mode..."
iwconfig $INTERFACE | grep -i "Mode:Monitor"

if [ $? -eq 0 ]; then
    echo "$INTERFACE is now in monitor mode and ready to use."
else
    echo "Failed to set $INTERFACE to monitor mode. Please check if your interface supports monitor mode."
fi

