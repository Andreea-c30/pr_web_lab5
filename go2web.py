import socket
import ssl
from bs4 import BeautifulSoup
import argparse
from urllib.parse import quote_plus

def https_request(url, max_redirects=5):
    try:
        #url parsing URL to get host and path
        url_parts = url.split('//')[-1].split('/')
        host = url_parts[0]
        path = '/' + '/'.join(url_parts[1:])
        port = 443 

        #create a socket 
        with socket.create_connection((host, port)) as client_socket:
            with ssl.create_default_context().wrap_socket(client_socket, server_hostname=host) as secure_socket:
                while max_redirects > 0:
                    request = f"GET {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"
                    secure_socket.sendall(request.encode())

                    response = b""
                    while True:
                        part = secure_socket.recv(1024)
                        if not part:
                            break
                        response += part

                    #redirection 
                    status_code = int(response.split()[1])
                    if 300 <= status_code < 400:
                        max_redirects -= 1
                        redirect_url = extract_redirect_url(response)
                        if not redirect_url:
                            print("error")
                            break
                        url_parts = urlparse(redirect_url)
                        host = url_parts.netloc
                        path = url_parts.path
                    else:
                        break

        if 200 <= status_code < 300:
            print("Success:")
        else:
            print("Failure:")

        #extract content
        try:
            html_content = response.decode('utf-8')
        except UnicodeDecodeError:
            html_content = response.decode('ISO-8859-1')
        
        soup = BeautifulSoup(html_content, 'html.parser')
        relevant_content = soup.get_text()

        print(relevant_content)

    except Exception as e:
        print("Error:", e)

def search_google(search_term):
    try:
        encoded_search = quote_plus(search_term)
        request_url = f"/search?q={encoded_search}"

        with socket.create_connection(("www.google.com", 80)) as client_socket:
            request = f"GET {request_url} HTTP/1.1\r\nHost: www.google.com\r\nConnection: close\r\n\r\n"
            client_socket.sendall(request.encode())

            response = b""
            while True:
                part = client_socket.recv(1024)
                if not part:
                    break
                response += part

        try:
            html_content = response.decode('utf-8')
        except UnicodeDecodeError:
            html_content = response.decode('ISO-8859-1')

        soup = BeautifulSoup(html_content, 'html.parser')
        count = 0
        for index, div in enumerate(soup.find_all('div', class_='egMi0 kCrYT'), 1):
            link_element = div.find('a', href=True)
            title_element = div.find('h3', class_='zBAuLc l97dzf')
            if link_element and title_element:
                title = title_element.get_text(strip=True)
                link = link_element['href']
                
                #extract only link from "http" until "/&"
                start_index = link.find("http")
                end_index = link.find("&")
                if start_index != -1 and end_index != -1:
                    link = link[start_index:end_index]
                
                print(index," - ", title," - ", link)
                

                count += 1
                if count >= 10:
                    break

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
        print("Input url or word")
