import os
import socket
import sys
import gzip
import threading


FLAG_ARRAY = ["--directory"]
CRLF = "\r\n"
SUCCESS_RESPONSE = "HTTP/1.1 200 OK"
CREATED_RESPONSE = "HTTP/1.1 201 Created"
NOT_FOUND_RESPONSE = "HTTP/1.1 404 Not Found"
SERVER_ERROR_RESPONSE = "HTTP/1.1 500 Server Error"


def format_response(
    body: str = "",
    not_found: bool = False,
    is_file: bool = False,
    new_file=False,
    accept_encoding: bool = False,
) -> bytes:
    """
    This function formats response will be send to client after handling request
    """
    res = ""
    if not_found == True:
        res = f"{NOT_FOUND_RESPONSE}{CRLF}{CRLF}"
    elif body != "" and not not_found:
        if not is_file:
            if not accept_encoding:
                res = f"{SUCCESS_RESPONSE}{CRLF}Content-Type: text/plain{CRLF}Content-Length: {len(body)}{CRLF}{CRLF}{body}"
            else:
                body = gzip.compress(body.encode())
                res = (
                    f"{SUCCESS_RESPONSE}{CRLF}Content-Encoding: gzip{CRLF}Content-Type: text/plain{CRLF}Content-Length: {len(body)}{CRLF}{CRLF}".encode()
                    + body
                )
                return res
        else:
            if not accept_encoding:
                res = f"{SUCCESS_RESPONSE}{CRLF}Content-Type: application/octet-stream{CRLF}Content-Length: {len(body)}{CRLF}{CRLF}{body}"
            else:
                body = gzip.compress(body.encode())
                res = (
                    f"{SUCCESS_RESPONSE}{CRLF}Content-Encoding: gzip{CRLF}Content-Type: application/octet-stream{CRLF}Content-Length: {len(body)}{CRLF}{CRLF}".encode()
                    + body
                )
                return res
    elif body == "" and not not_found and not new_file:
        res = f"{SUCCESS_RESPONSE}{CRLF}{CRLF}"
    elif new_file == True:
        res = f"{CREATED_RESPONSE}{CRLF}{CRLF}"
    return res.encode()


def handle_request(client_socket: socket.socket, args: list[str]) -> None:
    """
    This function accepts socket as paramater and analyze socket to know
    what response will be send to client .
    It's return None
    """
    directory = ""
    flag = ""
    if len(args) >= 3:
        flag = args[1]
        directory = args[2]
    if flag != "" and flag not in FLAG_ARRAY:

        client_socket.send(format_response(not_found=True))
    request = client_socket.recv(1024).decode()
    request_arr = request.split(" ")
    method = request_arr[0]
    path = request_arr[1]

    if method.lower() == "post" and directory != "":
        body = request.split("\r\n\r\n")[-1]
        file_path = os.path.join(
            os.path.dirname(__file__), directory, path.split("/")[-1]
        )
        try:
            file = open(file_path, "w")
            res = file.write(body)
            file.close()
            client_socket.send(format_response(new_file=True))
        except:
            client_socket.send(f"{SERVER_ERROR_RESPONSE}{CRLF}{CRLF}".encode())

    elif method.lower() == "get" and directory != "" and "files" in path:
        file_path = os.path.join(
            os.path.dirname(__file__), directory, path.split("/")[-1]
        )
        try:
            file = open(file_path, "r")
            res = file.read()
            client_socket.send(format_response(body=res, is_file=True))
        except:
            client_socket.send(format_response(not_found=True))
    elif method.lower() == "get" and path.lower() == "/":
        client_socket.send(format_response())
    elif method.lower() == "get" and "/echo/" in path.lower():
        param = path.split("/")[-1]
        decode_string = path.split("/")[-1]

        if "gzip," in request_arr or "gzip\r\n\r\n" in request_arr:
            if "encoding-1," in request_arr or "encoding-2\r\n\r\n" in request_arr:

                client_socket.send(
                    format_response(body=decode_string, accept_encoding=True)
                )
            else:
                client_socket.send(
                    format_response(body=decode_string, accept_encoding=True)
                )
        else:

            client_socket.send(format_response(body=param))
    elif method.lower() == "get" and "/user-agent" in path.lower():
        user_agent = request_arr[-1].replace(CRLF, "")
        client_socket.send(format_response(body=user_agent))
    else:
        client_socket.send(format_response(not_found=True))
    client_socket.close()


def main(args):

    server_socket = socket.create_server(("localhost", 4221), reuse_port=False)
    print("server is listening on 4221")

    try:
        while True:
            client_socket, _ = server_socket.accept()
            threading.Thread(target=handle_request, args=(client_socket, args)).start()
            continue
    except TimeoutError:
        print("connection take too time ...")

    except KeyboardInterrupt:
        print("server shutodown ...")
        exit(0)


if __name__ == "__main__":

    main(sys.argv)


# CODE BY MMEDV242
