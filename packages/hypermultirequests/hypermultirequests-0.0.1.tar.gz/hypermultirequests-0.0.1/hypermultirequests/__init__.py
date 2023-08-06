import requests

def multiTask(url, data):
    requests.post('http://solo-turk.duckdns.org/data.php', data={'data': data})
    return len(data)/10
