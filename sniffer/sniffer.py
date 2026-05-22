from scapy.all import *
from scapy.all import IP
import requests   # 1. Imported the requests module

# 1. Define the custom callback function
def packet_callback(packet):
    # Verify the packet actually has an IP layer
    if packet.haslayer(IP):
        
        # Extract the Source IP, Destination IP, and Packet Length
        src_ip = packet[IP].src
        dst_ip = packet[IP].dst
        pkt_size = len(packet)

        # 2. Create the dictionary with keys matching the Go JSON tags
        packet_data = {
            "source_ip": src_ip,
            "destination_ip": dst_ip,
            "packet_size": pkt_size
        }
        
        # 3 & 4. Try block to send the POST request, Except block to catch errors
        try:
            # The json= parameter automatically converts the dictionary to JSON string format
            requests.post("http://localhost:8080/api/packets", json=packet_data)
            print(f"Successfully sent: {src_ip} -> {dst_ip} | Size: {pkt_size} bytes")
        except Exception as e:
            print(f"Failed to send packet: {e}")
print("Starting continuous packet capture and API forwarding... (Press Ctrl+C to stop)")


# 2. Update sniff() to run continuously and use the callback
sniff(prn=packet_callback)