import socket


def main():

    print("Logs from your program will appear here!")

    server_socket = socket.create_server(("localhost", 4221), reuse_port=False)

    print("server is listening on 4221")
    response = "HTTP/1.1 200 OK\r\n\r\n"
    client_connection, client_address = server_socket.accept()
    print(f"connection form {client_address}")
    client_connection.sendall(response.encode())


if __name__ == "__main__":
    main()
