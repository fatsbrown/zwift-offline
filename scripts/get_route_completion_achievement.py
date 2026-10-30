#!/usr/bin/env python
import json
import os
import requests
import sys
import getpass
sys.path.insert(0, '../protobuf')
import route_completion_achievement_pb2
from google.protobuf.json_format import MessageToDict

def post_credentials(session, username, password):
    # Credentials POSTing and tokens retrieval
    # POST https://secure.zwift.com/auth/realms/zwift/tokens/access/codes
    try:
        response = session.post(
            url="https://secure.zwift.com/auth/realms/zwift/protocol/openid-connect/token",
            headers={
                "Accept": "*/*",
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive",
                "Content-Type": "application/x-www-form-urlencoded",
                "Host": "secure.zwift.com",
                "User-Agent": "Zwift/1.5 (iPhone; iOS 9.0.2; Scale/2.00)",
                "Accept-Language": "en-US;q=1",
            },
            data={
                "client_id": "Zwift_Mobile_Link",
                "username": username,
                "password": password,
                "grant_type": "password",
            },
            allow_redirects=False,
            verify=True,
        )

        if response.status_code != 200:
            print('Response HTTP Status Code: {status_code}'.format(
                status_code=response.status_code))
            print('Response HTTP Response Body: {content}'.format(
                content=response.content))

        json_dict = json.loads(response.content)

        return (json_dict["access_token"], json_dict["refresh_token"], json_dict["expires_in"])

    except requests.exceptions.RequestException as e:
        print('HTTP Request failed: %s' % e)

    except KeyError as e:
        print('Invalid uname and/or password')
        exit(-1)

def get_route_completion_achievement(session, access_token):
    try:
        response = session.get(
            url="https://us-or-rly101.zwift.com/api/achievement/route-completion-achievements",
            headers={
                "Accept-Encoding": "gzip, deflate",
                "Accept": "application/x-protobuf-lite",
                "Connection": "keep-alive",
                "Host": "us-or-rly101.zwift.com",
                "User-Agent": "Zwift/115 CFNetwork/758.0.2 Darwin/15.0.0",
                "Authorization": "Bearer %s" % access_token,
                "Accept-Language": "en-us",
            },
            verify=True,
        )

        if response.status_code != 200:
            print('Response HTTP Status Code: {status_code}'.format(
                status_code=response.status_code))

        return response.content

    except requests.exceptions.RequestException as e:
        print('HTTP Request failed: %s' % e)

def logout(session, refresh_token):
    # Logout
    # POST https://secure.zwift.com/auth/realms/zwift/tokens/logout
    try:
        response = session.post(
            url="https://secure.zwift.com/auth/realms/zwift/tokens/logout",
            headers={
                "Accept": "*/*",
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive",
                "Content-Type": "application/x-www-form-urlencoded",
                "Host": "secure.zwift.com",
                "User-Agent": "Zwift/1.5 (iPhone; iOS 9.0.2; Scale/2.00)",
                "Accept-Language": "en-US;q=1",
            },
            data={
                "client_id": "Zwift_Mobile_Link",
                "refresh_token": refresh_token,
            },
            verify=True,
        )
        if response.status_code != 204:
            print('Response HTTP Status Code: {status_code}'.format(
                status_code=response.status_code))
            print('Response HTTP Response Body: {content}'.format(
                content=response.content))
    except requests.exceptions.RequestException as e:
        print('HTTP Request failed: %s' % e)

def main(argv):
    username = input("Enter Zwift login (e-mail): ")
    if not sys.stdin.isatty():  # This terminal cannot support input without displaying text
        print(f'*WARNING* The current shell ({os.name}) cannot support hidden text entry.')
        print(f'Your password entry WILL BE VISIBLE.')
        print(f'If you are running a bash shell under windows, try executing this program via winpty:')
        print(f'>winpty python {argv[0]}')
        password = input("Enter password (will be shown):")
    else:
        password = getpass.getpass("Enter password: ")

    session = requests.session()
    access_token, refresh_token, expired_in = post_credentials(session, username, password)
    route_completion_achievement = route_completion_achievement_pb2.LoadPlayerRouteCompletionAchievementsResponse()
    route_completion_achievement.ParseFromString(get_route_completion_achievement(session, access_token))
    with open("../data/route_completion_achievement.txt", "w") as f:
        json.dump(MessageToDict(route_completion_achievement), f, indent=2)
    logout(session, refresh_token)


if __name__ == '__main__':
    try:
        main(sys.argv)
    except KeyboardInterrupt:
        pass
    except SystemExit as se:
        print("ERROR:", se)
