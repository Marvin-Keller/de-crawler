import socket
import csv
import ipaddress
import time
import requests
import re
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

def check_webpage(ip, port, time=5):
    url = f"http://{ip}:{str(port)}"
    info = {
        "title": "",
        "server": "",
        "fqdn": "",
        "exception": ""
    }

    try:
        res = requests.get(url, timeout=time)
        title = re.search('<title>(.+?)</title>', res.text)

        if title:
            info["title"] = title.group(1)
        
        info["server"] = str(res.headers.get("Server"))
        info["fqdn"] = socket.getnameinfo((str(ip), port), 0)[0]

    except requests.exceptions.ConnectTimeout:
        info["exception"] = "connecttimeouterror"

    except requests.exceptions.ReadTimeout:
        info["exception"] = "readtimeouterror"
    
    except requests.exceptions.ConnectionError:
        info["exception"] = "connectionerror"
    
    except requests.exceptions.InvalidURL:
        info["exception"] = "InvalidURLerror" + url

    except Exception as e:
        info["exception"] = type(e).__name__
    
    finally:
        return info


def checkPorts(fromIP, toIP, port, rIndex, db, comment=""):
    start_ip = ipaddress.IPv4Address(fromIP)
    end_ip = ipaddress.IPv4Address(toIP)

    IPscan = Query()

    for ip_int in range(int(start_ip), int(end_ip)):
        ip = str(ipaddress.IPv4Address(ip_int))

        if check_socket(ip, port):
            print(f"-- port {port} open: {ip}") 

            info = check_webpage(ip, port)
            db.upsert({
                'ip': ip, 
                'port': port, 
                'comment': comment, 
                'rowIndex': rIndex, 
                'timestamp': int(time.time()), 
                "info": info
                }, IPscan.ip == ip)
        else:
            print(f"-- port {port} closed: {ip}")
    
def buildSaveString(ip, port, provider):
    return f"{ip}:{port}, {provider}"

def main(): 
    port = 80
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
