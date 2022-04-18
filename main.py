import json
import requests
import re

base_url = "http://192.168.99.1/setup.cgi"
settings_file = 'settings.json'


def login(username, password):
    url = base_url + "?next_file=login_request"
    resp = requests.post(url, data={
        'submit_button': "login",
        'change_action': "",
        'action': "Apply",
        'wait_time': 19,
        'submit_type': "",
        'http_username': username,
        'http_passwd': password
    })
    text = str(resp.content, 'utf-8')
    return extract_session_id(text)


def extract_session_id(text):
    pattern = r'session_id\=([\w|\d]+)'
    match = re.findall(pattern, text)
    return match[0]


def connection_request(session, currentStatus, todo):
    url = base_url + "?session_id=" + session
    data = {
        'ctype': 'pppoe',
        'ifstatus': currentStatus,
        'todo': todo,
        'this_file': 'Status.htm',
        'next_file': 'Status.htm',
        'message': '',
        'h_session_id': session,
        'h_wps_cur_status': ''
    }
    return requests.post(url, data=data)


def disconnect(session):
    current_status = "Up"
    todo = "disconnect"
    connection_request(session, current_status, todo)


def connect(session):
    current_status = "Down"
    todo = "connect"
    connection_request(session, current_status, todo)


# Retrieve the IP
def get_IP():
    provider = "https://checkip.amazonaws.com"
    resp = requests.get(provider)
    extractedIP = str(resp.content, 'utf-8').strip()
    return extractedIP


if __name__ == '__main__':
    with open(settings_file, "r") as f:
        settings = json.load(f)
    #Get old ip
    old_ip = get_IP()
    print("Current IP: " + old_ip)
    # Login
    token = login(settings["user"], settings["psw"])
    # Disconnect
    print("Disconnecting...")
    disconnect(token)
    # Connect
    print("Reconnecting...")
    connect(token)
    #Get new IP
    new_ip = get_IP()
    print("Old IP: " + old_ip + " -> new IP: " + new_ip)
