import socket
import datetime
import configparser

# Global state for the server
server_state = {
    'is_edit': False,
    'current_list_id': None,
    'lists': {},
    'log_file': 'server_log.txt'
}

def get_server_port(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)
    return int(config['DEFAULT']['ServerPort'])

def log_message(message, log_type, address=None):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"{timestamp} - {log_type} - {address if address else 'Server'}: {message}"
    with open(server_state['log_file'], 'a') as log_file:
        log_file.write(log_entry + "\n")
    print(log_entry)

def get_valid_commands():
    return 'Valid commands are:\n' \
           'CATALOG\n' \
           'CREATE <list title>\n' \
           'EDIT <list number>\n' \
           'DISPLAY <list number>\n' \
           'DELETE <list number>\n' \
           'SHOW\n' \
           'ADD <list item text>\n' \
           'REMOVE <list item number>\n' \
           'QUIT\n' \
           'EXIT'

def process_command(request, client_address):
    global server_state
    parts = request.split()
    command = parts[0].lower()
    args = parts[1:]

    def handle_edit_mode():
        if command == 'show':
            return ' '.join(server_state['lists'][server_state['current_list_id']])
        elif command == 'add' and args:
            item = ' '.join(args)
            server_state['lists'][server_state['current_list_id']].append(item)
            return f'Added item: {item}'
        elif command == 'remove' and args:
            try:
                index = int(args[0])
                item = server_state['lists'][server_state['current_list_id']].pop(index)
                return f'Removed item: {item}'
            except (IndexError, ValueError):
                return 'Invalid index.'
        elif command == 'quit':
            server_state['is_edit'] = False
            return 'Exited edit mode.'
        else:
            return 'Invalid command in edit mode.'

    if server_state['is_edit']:
        return handle_edit_mode()
    
    if command == 'catalog':
        if server_state['lists']:
            return ', '.join([f'{id}: {data[0]}' for id, data in server_state['lists'].items()])
        else:
            return 'No lists available'
    elif command == 'create':
        if not args:
            return 'Missing element: CREATE\nusage: CREATE <list title>'
        list_name = ' '.join(args)
        list_id = max(server_state['lists'].keys(), default=0) + 1
        server_state['lists'][list_id] = [list_name]
        return f'List created: {list_name} with ID {list_id}'
    elif command == 'edit':
        if not args:
            return 'Missing element: EDIT\nusage: EDIT <list number>'
        try:
            server_state['current_list_id'] = int(args[0])
            server_state['is_edit'] = True
            return f'Editing list ID {server_state["current_list_id"]}'
        except ValueError:
            return 'Invalid list ID.'
    elif command == 'display':
        if not args:
            return 'Missing element: DISPLAY\nusage: DISPLAY <list number>'
        try:
            list_id = int(args[0])
            return ' '.join(server_state['lists'][list_id])
        except (KeyError, ValueError):
            return 'List does not exist.'
    elif command == 'delete':
        if not args:
            return 'Missing element: DELETE\nusage: DELETE <list number>'
        try:
            list_id = int(args[0])
            del server_state['lists'][list_id]
            return f'Deleted list ID {list_id}'
        except KeyError:
            return 'List does not exist.'
    elif command == 'exit':
        return 'Shutting down server.'
    else:
        return f'Invalid command: {command}.\n{get_valid_commands()}'

def handle_client(connection, client_address):
    while True:
        request = connection.recv(1024).decode()
        if not request:
            break
        log_message(request, 'Request', client_address)
        response = process_command(request, client_address)
        log_message(response, 'Response')
        connection.sendall(response.encode())
    connection.close()

def start_server(port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', port))
    server_socket.listen(5)
    log_message(f'Starting server on port {port}', 'Info')

    while True:
        client_socket, client_address = server_socket.accept()
        handle_client(client_socket, client_address)

if __name__ == '__main__':
    port = get_server_port('config.txt')
    start_server(port)
