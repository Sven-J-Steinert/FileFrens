import argparse
import subprocess
from tqdm import tqdm
import socket
import os

port = 4444

alias = {
    'sven':"172.23.221.18",
    'niklas':"172.23.54.175",
    'christoph':"172.23.214.213",
    'nikolai':"172.23.182.187",
}

SEPARATOR = "<SEPARATOR>"
BUFFER_SIZE = 4096

def ping(ip):
    try:
        # Use the ping command to check if the IP is reachable
        cmd = f'ping -n 1 "{ip}"'
        subprocess.check_output(cmd, stderr=subprocess.STDOUT,shell=True).decode('iso8859-1')
        return True
    except subprocess.CalledProcessError as e:
        return False
    
def readable(bool):
    if bool: return "passed"
    if not bool: return "failed"
    else: return None

def send_file(filename, ip):
    if ip.lower() in alias: ip = alias[ip.lower()]
    # Implement the logic to send the file to the specified IP address here
    print(f"Sending {filename} to {ip}")
    print(f'Network check {readable(ping(ip))}')
    s = socket.socket()
    s.connect((ip, port))
    print("connected")
    filesize = os.path.getsize(filename)
    s.send(f"{filename}{SEPARATOR}{filesize}".encode())
    print("start sending")
    progress = tqdm.tqdm(range(filesize), f"Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024)
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

    s.close()


def receive_file(path, ip):
    if ip.lower() in alias: ip = alias[ip.lower()]
    # Implement the logic to receive the file from the specified IP address here
    print(f"Receiving file from {ip} to path: {path}")
    print(f'Network check {readable(ping(ip))}')
    s = socket.socket()
    s.bind(("0.0.0.0", port))
    s.listen(5)
    print(f"[*] Listening ")
    client_socket, address = s.accept() 
    # if below code is executed, that means the sender is connected
    print(f"[+] {address} is connected.")
    # receive the file infos
    # receive using client socket, not server socket
    received = client_socket.recv(BUFFER_SIZE).decode()
    filename, filesize = received.split(SEPARATOR)
    # remove absolute path if there is
    filename = os.path.basename(filename)
    # convert to integer
    filesize = int(filesize)
    progress = tqdm.tqdm(range(filesize), f"Receiving {filename}", unit="B", unit_scale=True, unit_divisor=1024)
    with open(filename, "wb") as f:
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

    # close the client socket
    client_socket.close()
    # close the server socket
    s.close()

def main():
    parser = argparse.ArgumentParser(description="Send or receive files with filefrens")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-s", "--send", nargs=2, metavar=("FILE", "IP"), help="Send a file")
    group.add_argument("-r", "--receive", nargs=2, metavar=("PATH", "IP"), help="Receive a file")

    args = parser.parse_args()

    if args.send:
        send_file(args.send[0], args.send[1])
    elif args.receive:
        receive_file(args.receive[0], args.receive[1])

if __name__ == "__main__":
    main()
