import os
import socket
import sys
import gzip

FLAG_ARRAY = ["--directory"]
CRLF = "\r\n"
SUCCESS_RESPONSE = "HTTP/1.1 200 OK"
CREATED_RESPONSE = "HTTP/1.1 201 Created"
NOT_FOUND_RESPONSE = "HTTP/1.1 404 Not Found"
SERVER_ERROR_RESPONSE = "HTTP/1.1 500 Server Error"


def format_response(
    body: str = "",
    status: str = SUCCESS_RESPONSE,
    content_type: str = "text/plain",
    accept_encoding: bool = False,
) -> bytes:
    """
    This function formats the response to be sent to the client after handling a request.
    """
    headers = [
        f"{status}",
        f"Content-Type: {content_type}",
        f"Content-Length: {len(body)}",
    ]

    if accept_encoding:
        body = gzip.compress(body.encode())
        headers.append(f"Content-Encoding: gzip")

    response = f"{CRLF.join(headers)}{CRLF}{CRLF}".encode()

    if isinstance(body, str):
        response += body.encode()
    else:
        response += body

    return response


def handle_post_request(
    client_socket: socket.socket, directory: str, path: str, body: str
) -> None:
    """
    Handle a POST request to write a file.
    """
    file_path = os.path.join(os.path.dirname(__file__), directory, path.split("/")[-1])
    try:
        with open(file_path, "w") as file:
            file.write(body)
        client_socket.send(format_response(status=CREATED_RESPONSE))
    except Exception as e:
        print(f"Error writing file: {e}")
        client_socket.send(format_response(status=SERVER_ERROR_RESPONSE))


def handle_get_request(
    client_socket: socket.socket, directory: str, path: str, request: str
) -> None:
    """
    Handle a GET request to read a file or echo a message.
    """
    if path == "/":
        client_socket.send(format_response())
    elif "files" in path:
        file_path = os.path.join(
            os.path.dirname(__file__), directory, path.split("/")[-1]
        )
        try:
            with open(file_path, "r") as file:
                content = file.read()
            client_socket.send(
                format_response(body=content, content_type="application/octet-stream")
            )
        except FileNotFoundError:
            client_socket.send(format_response(status=NOT_FOUND_RESPONSE))
    elif "/echo/" in path:
        message = path.split("/")[-1]
        accept_encoding = "gzip" in request
        client_socket.send(
            format_response(body=message, accept_encoding=accept_encoding)
        )
    elif "/user-agent" in path:
        user_agent = request.split("\r\n")[-1]
        client_socket.send(format_response(body=user_agent))
    else:
        client_socket.send(format_response(status=NOT_FOUND_RESPONSE))


def handle_request(client_socket: socket.socket, args: list[str]) -> None:
    """
    Analyze the request and send the appropriate response to the client.
    """
    if len(args) < 3 or args[1] not in FLAG_ARRAY:
        client_socket.send(format_response(status=NOT_FOUND_RESPONSE))
        return

    directory = args[2]
    request = client_socket.recv(1024).decode()
    request_lines = request.split(CRLF)
    method, path, _ = request_lines[0].split(" ")

    if method.lower() == "post":
        body = request.split(CRLF + CRLF)[-1]
        handle_post_request(client_socket, directory, path, body)
    elif method.lower() == "get":
        handle_get_request(client_socket, directory, path, request)
    else:
        client_socket.send(format_response(status=NOT_FOUND_RESPONSE))

    client_socket.close()


def main(args):
    server_socket = socket.create_server(("localhost", 4221), reuse_port=False)
    print("Server is listening on port 4221")

    try:
        while True:
            client_socket, _ = server_socket.accept()
            handle_request(client_socket, args)
    except TimeoutError:
        print("Connection took too long...")
    except KeyboardInterrupt:
        print("Server shutdown...")
    finally:
        server_socket.close()
        exit(0)


if __name__ == "__main__":
    main(sys.argv)

# CODE BY MMEDV242
