import socket

CRLF = "\r\n"

SUCCESS_RESPONSE = "HTTP/1.1 200 OK"
NOT_FOUND_RESPONSE = "HTTP/1.1 404 Not Found"


def handle_request(client_socket: socket.socket) -> None:

    request = client_socket.recv(1024).decode()

    request_arr = request.split(" ")
    print(request_arr)
    method = request_arr[0]
    path = request_arr[1]
    http_version = request_arr[2]

    if method.lower() == "get" and path.lower() == "/":
        client_socket.send(f"SUCCESS_RESPONSE{CRLF}{CRLF}".encode())
    elif method.lower() == "get" and "/echo/" in path.lower():
        param = path.split("/")[-1]
        response = f"SUCCESS_RESPONSE{CRLF}Content-Type: text/plain{CRLF}Content-Length: {len(param)}{CRLF}{CRLF}{param}"
        client_socket.send(response.encode())
    else:
        client_socket.send(f"NOT_FOUND_RESPONSE{CRLF}{CRLF}".encode())
    client_socket.close()


def main():

    print("Logs from your program will appear here!")
    server_socket = socket.create_server(("localhost", 4221), reuse_port=False)
    print("server is listening on 4221")

    client_socket, _ = server_socket.accept()
    handle_request(client_socket)


if __name__ == "__main__":
    main()
