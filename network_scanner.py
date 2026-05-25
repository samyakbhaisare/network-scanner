import scapy.all as scapy
import socket
import threading
from queue import Queue
import ipaddress

def scan(ip, result_queue):
    arp_request = scapy.ARP(pdst=ip)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = broadcast/arp_request
    answer = scapy.srp(packet, timeout=1, verbose=False)[0]

    clients = []
    for client in answer:
        client_info = {'IP': client[1].psrc, 'MAC': client[1].hwsrc}
        try:
            hostname = socket.gethostbyaddr(client_info['IP'])[0]
            client_info['Hostname'] = hostname
        except socket.herror:
            client_info['Hostname'] = 'Unknown'
        clients.append(client_info)
    result_queue.put(clients)

def print_result(result):
    print(f"{'IP':<18} {'MAC':<20} {'Hostname'}")
    print("-" * 60)
    for client in result:
        print(f"{client['IP']:<18} {client['MAC']:<20} {client['Hostname']}")

def save_results(result):
    with open("network_scan_results.txt", "w") as file:
        file.write(f"{'IP':<18} {'MAC':<20} {'Hostname'}\n")
        file.write("-" * 60 + "\n")
        for client in result:
            file.write(f"{client['IP']:<18} {client['MAC']:<20} {client['Hostname']}\n")
    print("\n[+] Results saved to network_scan_results.txt")

def main(cidr):
    result_queue = Queue()
    threads = []
    network = ipaddress.ip_network(cidr, strict=False)

    for ip in network.hosts():
        thread = threading.Thread(target=scan, args=(str(ip), result_queue))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    all_clients = []
    while not result_queue.empty():
        all_clients.extend(result_queue.get())
        
    print_result(all_clients)
    save_results(all_clients)

if __name__ == "__main__":
    cidr = input("Enter network ip address:")
    main(cidr)
