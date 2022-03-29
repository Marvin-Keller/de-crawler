import socket
import csv
import ipaddress
import time
from contextlib import closing
from tinydb import TinyDB, Query

TIMEOUT = 0.5
MAX_PROCESSES = 2

def check_socket(host, port):
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        sock.settimeout(TIMEOUT)
        if sock.connect_ex((host, port)) == 0:
            return True
        else:
            return False

def checkPorts(fromIP, toIP, port, rIndex, db, info="- no info"):
    start_ip = ipaddress.IPv4Address(fromIP)
    end_ip = ipaddress.IPv4Address(toIP)

    IPscan = Query()

    for ip_int in range(int(start_ip), int(end_ip)):
        ip = str(ipaddress.IPv4Address(ip_int))

        if check_socket(ip, port):
            print(f"-- port {port} open: {ip}") 
            db.upsert({'ip': ip, 'port': port, 'info': info, 'rowIndex': rIndex, 'timestamp': int(time.time())}, IPscan.ip == ip)
        else:
            print(f"-- port {port} closed: {ip}")
    
def buildSaveString(ip, port, provider):
    return f"{ip}:{port}, {provider}"

def main(): 
    port=80
    db = TinyDB('./db/db.json')

    with open('./crawling-data/de-1.csv', newline='') as csvfile:
        csvData = csv.reader(csvfile, delimiter=',', quotechar='|')
        rowIndex = 0
    
        for row in csvData:
            rowIndex+=1
            
            print(f"start row {rowIndex}: {row[4]}")
            checkPorts(row[0], row[1], port, rowIndex, db, row[4])
            print(f"finished row {rowIndex}: {row[4]}")
            print("")
        

if __name__ == "__main__": 
	main() 
