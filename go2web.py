import socket
import ssl
from bs4 import BeautifulSoup
import argparse
from urllib.parse import quote_plus

def https_request(url):
    try:
        # Parse the URL to get host and path
        url_parts = url.split('//')[-1].split('/')
        host = url_parts[0]
        path = '/' + '/'.join(url_parts[1:])
        port = 443  # Default HTTPS port

        # Create a socket object
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Wrap the socket with SSL context
        ssl_context = ssl.create_default_context()
        client_socket = ssl_context.wrap_socket(client_socket, server_hostname=host)

        # Connect to the server
        client_socket.connect((host, port))

        # Form the HTTPS request
        request = f"GET {path} HTTP/1.1\r\nHost: {host}\r\n\r\n"

        # Send the request
        client_socket.sendall(request.encode())

        # Receive the response
        response = b""
        while True:
            part = client_socket.recv(1024)
            if not part:
                break
            response += part

        # Check for success or failure
        status_code = int(response.decode().split()[1])
        if 200 <= status_code < 300:
            print("Success Response:")
        else:
            print("Failure Response:")

        # Print the response
        html_content = response.decode()

        # Use Beautiful Soup to extract relevant content
        soup = BeautifulSoup(html_content, 'html.parser')
        relevant_content = soup.get_text()

        print(relevant_content)

        # Close the socket
        client_socket.close()
    except Exception as e:
        print("Error:", e)

def search_google(search_term):
    try:
        encoded_search = quote_plus(search_term)
        request_url = f"/search?q={encoded_search}"

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        client_socket.connect(("www.google.com", 80))

        host = "www.google.com"
        request = f"GET {request_url} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"
        client_socket.sendall(request.encode())

        # Receive the response
        response = b""
        while True:
            part = client_socket.recv(1024)
            if not part:
                break
            response += part

        # Close the socket
        client_socket.close()

        try:
            html_content = response.decode('utf-8')
        except UnicodeDecodeError:
            html_content = response.decode('ISO-8859-1')

        soup = BeautifulSoup(html_content, 'html.parser')
        res = soup.find_all("h3") 
        #print(res)
        for div in res:
            search_results = res 
            if search_results:
                for i, result in enumerate(search_results[:10], 1):
                    print(i, result.get_text())
                break  
        else:
            print("No search results found.")
    except Exception as e:
        print("Error:", e)


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description="Creating HTTP requests and retrieving content from websites")
    parser.add_argument("-u", "--url", help="Make an HTTP request to the specified URL and print the response")
    parser.add_argument("-s", "--search", help="Make an HTTP request to search the term using your favorite search engine and print top 10 results")
    args = parser.parse_args()

    if args.url:
        https_request(args.url)
    elif args.search:
        search_google(args.search)
 
    else:
        print("Please provide either a URL or a search term.")
