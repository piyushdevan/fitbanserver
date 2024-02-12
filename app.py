import socket
import threading
import time

HOST = "0.0.0.0"
PORT = 8888
RECONNECT_DELAY = 5  # Delay in seconds before attempting to reconnect
MAX_READINGS = 1000  # Maximum number of readings to receive at once
BUFFER_SIZE = 4096  # Buffer size for receiving data

server_socket = None
buffer_lock = threading.Lock()
buffered_data = []
running = True


def receive_data(conn):
    readings_received = 0
    while readings_received < MAX_READINGS:
        try:
            data = conn.recv(BUFFER_SIZE)
            if not data:
                break
            sensor_data = data.decode("utf-8")
            print("Received sensor data:", sensor_data)
            with buffer_lock:
                buffered_data.append(sensor_data)
                with open("sensor_data.csv", "a") as f:
                    f.write(sensor_data)
            readings_received += 1
            conn.sendall(b"Data received by server")
        except Exception as e:
            print(f"Error occurred while receiving data: {e}")
            return False
    return True


def handle_client(conn, addr):
    print("Connected by", addr)
    while receive_data(conn):
        pass
    conn.close()


def start_server():
    global server_socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((HOST, PORT))
            s.listen()
            print("Server listening on", HOST, ":", PORT)
            server_socket = s
            while running:
                conn, addr = s.accept()
                thread = threading.Thread(target=handle_client, args=(conn, addr))
                thread.start()
        except Exception as e:
            print(f"Error occurred while starting server: {e}")
            restart_server()


def stop_server():
    global server_socket, running
    running = False
    if server_socket:
        server_socket.close()


def restart_server():
    print(f"Restarting server in {RECONNECT_DELAY} seconds...")
    stop_server()
    time.sleep(RECONNECT_DELAY)
    start_server()


if __name__ == "__main__":
    start_server()
