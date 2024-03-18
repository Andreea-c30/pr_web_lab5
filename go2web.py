import socket
import ssl

def make_https_request(url):
    try:
        host, path = parse_url(url)
        
        with socket.create_connection((host, 443)) as sock:
            with ssl.create_default_context().wrap_socket(sock, server_hostname=host) as ssock:
                request = f"GET {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"
                ssock.sendall(request.encode())

                response = b""
                while True:
                    data = ssock.recv(1024)
                    if not data:
                        break
                    response += data

                return response.decode()
    except Exception as e:
        print("Error making HTTPS request:", e)
        return None

def parse_url(url):
    if url.startswith("https://"):
        url = url[len("https://"):]

    parts = url.split("/", 1)
    host = parts[0]
    path = "/" + parts[1] if len(parts) > 1 else "/"
    
    return host, path

def print_response(response_text):
    if response_text:
        print(response_text)

if __name__ == "__main__":
    url = "https://999.md/ro/category/transport"
    response_text = make_https_request(url)
    print_response(response_text)
