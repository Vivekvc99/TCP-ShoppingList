import socket
import configparser

def read_config(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)
    return config['DEFAULT']['ServerIP'], int(config['DEFAULT']['ServerPort'])

def send_request(server_ip, server_port, request):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.connect((server_ip, server_port))
            sock.sendall(request.encode())
            response = sock.recv(4096)
            return response.decode()
        except Exception as e:
            return f"Error: {e}"

def main():
    server_ip, server_port = read_config('config.txt')
    print(f"Connecting to server at {server_ip}:{server_port}")

    while True:
        command = input("Enter command (type 'exit' to quit): ")
        if command.lower() == 'exit':
            break
        response = send_request(server_ip, server_port, command)
        print("Server response:", response)

if __name__ == "__main__":
    main()
