import socket
import json


# Live status helper function - returns JSON object,
# address is either path to the live status pipe or
# a tuple (host, port) for remote connection
def query(address, request):
    sock = None
    try:
        if len(address) == 2:
            host_addr = socket.getaddrinfo(address[0], 80, 0, 0, socket.IPPROTO_TCP)
            ip6 = filter(lambda x: x[0] == socket.AF_INET6, host_addr)
            if ip6:
                sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
            else:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect(address)
        if 'OutputFormat: json\nColumnHeaders: on\n' not in request:
            request += '\nOutputFormat: json\nColumnHeaders: on\n'
        sock.send(request)
        sock.shutdown(socket.SHUT_WR)
        rawdata = sock.makefile().read()
        if not rawdata:
            return []
        data = json.loads(rawdata)
        return [dict(zip(data[0], value)) for value in data[1:]]
    finally:
        if sock:
            sock.close()
