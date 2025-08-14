import threading
from datetime import datetime
from scapy.all import sniff, IP, TCP, UDP
import pandas as pd
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PacketProcessor:
    def __init__(self):
        self.protocol_map = {1: 'ICMP', 6: 'TCP', 17: 'UDP'}
        self.packet_data = []
        self.start_time = datetime.now()
        self.packet_count = 0
        self.lock = threading.Lock()

    def get_protocol_name(self, protocol_num):
        return self.protocol_map.get(protocol_num, f'OTHER({protocol_num})')

    def process_packet(self, packet):
        try:
            if IP in packet:
                with self.lock:
                    packet_info = {
                        'timestamp': datetime.now().isoformat(),
                        'source': packet[IP].src,
                        'destination': packet[IP].dst,
                        'protocol': self.get_protocol_name(packet[IP].proto),
                        'size': len(packet),
                        'time_relative': (datetime.now() - self.start_time).total_seconds()
                    }
                    if TCP in packet:
                        packet_info.update({
                            'src_port': packet[TCP].sport,
                            'dst_port': packet[TCP].dport,
                            'tcp_flags': str(packet[TCP].flags)
                        })
                    elif UDP in packet:
                        packet_info.update({
                            'src_port': packet[UDP].sport,
                            'dst_port': packet[UDP].dport
                        })
                    self.packet_data.append(packet_info)
                    self.packet_count += 1
                    if len(self.packet_data) > 10000:
                        self.packet_data.pop(0)
        except Exception as e:
            print(f"Error processing packet: {e}")

    def get_dataframe(self):
        with self.lock:
            return pd.DataFrame(self.packet_data)


def start_packet_capture():
    processor = PacketProcessor()
    def capture_packets():
        sniff(prn=processor.process_packet, store=False)
    capture_thread = threading.Thread(target=capture_packets, daemon=True)
    capture_thread.start()
    return processor
