import argparse
import subprocess
from tqdm import tqdm
import socket
import os
import requests
import hashlib
import json

version = '1.0.0'

def readable(bool):
    if bool: return "\033[32mpassed\033[0m"
    if not bool: return "\033[31mfailed\033[0m"
    else: return None

url = "https://raw.githubusercontent.com/Sven-J-Steinert/Filefrens/main/alias.json"

port = 4444

SEPARATOR = "<SEPARATOR>"
BUFFER_SIZE = 4096*8
TIMEOUT = 1

def ping(ip):
    try:
        # Use the ping command to check if the IP is reachable
        cmd = f'ping -n 1 "{ip}"'
        subprocess.check_output(cmd, stderr=subprocess.STDOUT,shell=True).decode('iso8859-1')
        return True
    except subprocess.CalledProcessError as e:
        return False
    
def create_checksum(filename,msg):

    sha1 = hashlib.sha1()

    filesize = os.path.getsize(filename)
    progress = tqdm(range(filesize),msg,unit="B", unit_scale=True, unit_divisor=1024, leave=False)
    with open(filename, 'rb') as f:
        while True:
            data = f.read(BUFFER_SIZE)
            if not data:
                break
            sha1.update(data)
            progress.update(len(data))
        progress.close()

    checksum = sha1.hexdigest()

    return checksum

def send_file(filename, ip):

    if ip.lower() in alias: ip = alias[ip.lower()]

    print(f'Network check {readable(ping(ip))}')
          
    checksum = create_checksum(filename,'Creating checksum ')

    print(f"Creating checksum \033[32mdone\033[0m SHA1: {checksum}")

    sec = 0
    msg = f'Waiting for reciever {sec:5.0f}s '
    print(msg, end="\r", flush=True)

    while True:
        try:
            s = socket.socket()
            s.settimeout(TIMEOUT)
            s.connect((ip, port))
            print("Waiting for reciever \033[32mconnected\033[0m")
            break
        except Exception as e:
            sec += 1
            msg = f'Waiting for reciever {sec:5.0f}s '
            print(msg, end="\r", flush=True)
            pass

    filesize = os.path.getsize(filename)

    s.send(f"{filename}{SEPARATOR}{filesize}{SEPARATOR}{checksum}".encode())
    print(f"Sending {filename}")
    progress = tqdm(range(filesize), unit="B", unit_scale=True, unit_divisor=1024)
    with open(filename, "rb") as f:
        while True:
            # read the bytes from the file
            bytes_read = f.read(BUFFER_SIZE)
            if not bytes_read:
                # file transmitting is done
                break
            # we use sendall to assure transimission in 
            # busy networks
            s.sendall(bytes_read)
            # update the progress bar
            progress.update(len(bytes_read))
        progress.close()

    s.close()

def receive_file(path, ip):
    if ip.lower() in alias: ip = alias[ip.lower()]
    # Implement the logic to receive the file from the specified IP address here
    print(f"Receiving file from {ip} to path: {path}")
    print(f'Network check {readable(ping(ip))}')
    
    sec = 0
    msg = f'Listening {sec:5.0f}s '
    print(msg, end="\r", flush=True)

    while True:
        try:
            s = socket.socket()
            s.bind(("0.0.0.0", port))
            s.settimeout(TIMEOUT)
            s.listen()
            client_socket, address = s.accept() 
            
            print(f"Listening \033[32mconnected\033[0m {address}")
            break
        except Exception as e:
            sec += 1
            msg = f'Listening {sec:5.0f}s '
            print(msg, end="\r", flush=True)
            pass
    
    # receive the file infos
    # receive using client socket, not server socket
    received = client_socket.recv(BUFFER_SIZE).decode()
    filename, filesize, checksum = received.split(SEPARATOR)
    # remove absolute path if there is
    filename = os.path.basename(filename)
    # convert to integer
    filesize = int(filesize)
    print(f"Receiving {filename}")
    progress = tqdm(range(filesize), unit="B", unit_scale=True, unit_divisor=1024)
    with open(f"{path}/{filename}", "wb") as f:
        while True:
            # read 1024 bytes from the socket (receive)
            bytes_read = client_socket.recv(BUFFER_SIZE)
            if not bytes_read:    
                # nothing is received
                # file transmitting is done
                break
            # write to the file the bytes we just received
            f.write(bytes_read)
            # update the progress bar
            progress.update(len(bytes_read))
        progress.close()

    # close the client socket
    client_socket.close()
    # close the server socket
    s.close()

    file_checksum = create_checksum(f'{path}/{filename}','Validating checksum ')
    print(f'Validating checksum {readable(checksum == file_checksum)}')


def main():
    parser = argparse.ArgumentParser(description="Send or receive files with filefrens")
    parser.add_argument("IP", metavar="IP", help="IP address (required)")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-s", "--send", nargs=1, metavar=("FILE"), help="Send a file")
    group.add_argument("-r", "--receive", nargs=1, metavar=("PATH"), help="Receive a file")
    group.add_argument("-v", "--version", nargs=1, help="show version")

    args = parser.parse_args()

    if args.send:
        send_file(args.send[0], args.IP)
    elif args.receive:
        receive_file(args.receive[0], args.IP)
    elif args.version:
        print(f'FileFrens Version {version}')


print("Updating alias list",end=" ")
try:
    response = requests.get(url)
    if response.status_code == 200:
        alias = json.loads(response.text)
        print(readable(True))
    else:
        print(f"Failed to retrieve the file. Status code: {response.status_code}")
except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
