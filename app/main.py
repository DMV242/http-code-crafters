import socket

CRLF = "\r\n"
SUCCESS_RESPONSE = "HTTP/1.1 200 OK"
NOT_FOUND_RESPONSE = "HTTP/1.1 404 Not Found"


def format_response(body: str = "", not_found: bool = False) -> bytes:
    """
    This function formats response will be send to client after handling request
    """
    res = ""

    if body != "" and not_found == False:
        res = f"{SUCCESS_RESPONSE}{CRLF}Content-Type: text/plain{CRLF}Content-Length: {len(body)}{CRLF}{CRLF}{body}"
    if not_found == True:
        res = f"{NOT_FOUND_RESPONSE}{CRLF}{CRLF}"
    if body == "" and not not_found:
        res = f"{SUCCESS_RESPONSE}{CRLF}{CRLF}"
    return res.encode()


def handle_request(client_socket: socket.socket) -> None:
    """
    This function accepts socket as paramater and analyze socket to know
    what response will be send to client .
    It's return None
    """
    request = client_socket.recv(1024).decode()
    request_arr = request.split(" ")
    method = request_arr[0]
    path = request_arr[1]

    if method.lower() == "get" and path.lower() == "/":
        client_socket.send(format_response())
    elif method.lower() == "get" and "/echo/" in path.lower():
        param = path.split("/")[-1]
        client_socket.send(format_response(body=param))
    elif method.lower() == "get" and "/user-agent" in path.lower():
        user_agent = request_arr[-1].replace(CRLF, "")
        client_socket.send(format_response(body=user_agent))
    else:
        client_socket.send(format_response(not_found=True))
    client_socket.close()


def main():

    print("Logs from your program will appear here!")
    server_socket = socket.create_server(("localhost", 4221), reuse_port=False)
    print("server is listening on 4221")

    while True:
        try:
            client_socket, _ = server_socket.accept()
            handle_request(client_socket)
            continue
        except TimeoutError:
            print("connection take too time ...")
            continue
        except KeyboardInterrupt:
            print("server shutodown ...")
            exit(0)


if __name__ == "__main__":
    main()
