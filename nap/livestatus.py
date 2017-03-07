import socket
import json


# Live status helper function - returns JSON object,
# address is either path to the live status pipe or
# a tuple (host, port) for remote connection
def query(address, request):
    try:
        if len(address) == 2:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.connect(address)
        if 'OutputFormat: json\nColumnHeaders: on\n' not in request:
            request += '\nOutputFormat: json\nColumnHeaders: on\n'
        s.send(request)
        s.shutdown(socket.SHUT_WR)
        rawdata = s.makefile().read()
        if not rawdata:
            return []
        data = json.loads(rawdata)
        return [dict(zip(data[0], value)) for value in data[1:]]
    finally:
        s.close()
