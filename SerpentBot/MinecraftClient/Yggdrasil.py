import requests
import json
import uuid

class Yggdrasil:
    server_address = "https://authserver.mojang.com"
    @classmethod
    def prepare (self, credential_file):
        with open (credential_file, "r") as actual_credential_file: credential_data = json.load (actual_credential_file)
        if "client_token" not in credential_data.keys ():
            # generate a new client token since we don't have one
            credential_data ["client_token"] = uuid.uuid4 ().hex
        reauthenticate = True
        if "access_token" in credential_data.keys ():
            # we have an existing access token, check if it's still usable
            status_code, _json = Yggdrasil._send_request (endpoint = "/validate", payload = {
                "accessToken": credential_data ["access_token"],
                "clientToken": credential_data ["client_token"]
            })
            if not (status_code == 204):
                # we need to refresh the access token to make it usable
                status_code, _json = Yggdrasil._send_request (endpoint = "/refresh", payload = {
                    "accessToken": credential_data ["access_token"],
                    "clientToken": credential_data ["client_token"],
                    "selectedProfile": {},
                    "requestUser": False # we don't need the user object in the response
                })
                if status_code != 200: # refreshing the access token failed
                    reauthenticate = True
                else: # refreshing the access token succeeded!
                    credential_data ["access_token"] = _json ["accessToken"]
                    reauthenticate = False
            else:
                # otherwise existing access token is still usable
                reauthenticate = False
        else:
            reauthenticate = True # no access token, probably first time logging in
        if reauthenticate: # get a completely fresh access token
            assert "username" in credential_data and "password" in credential_data, "Username and/or password not specified in credentials file, but necessary due to lack of valid access token"
            status_code, _json = Yggdrasil._send_request (endpoint = "/authenticate", payload = {
                "agent": {
                    "name": "Minecraft",
                    "version": 1
                }, # matches vanilla
                "username": credential_data ["username"],
                "password": credential_data ["password"],
                "clientToken": credential_data ["client_token"],
                "requestUser": False # we don't need the user object in the response
            })
            assert status_code == 200, f"Failed to authenticate with Yggdrasil: {json ['errorMessage']}"
            credential_data ["access_token"] = _json ["accessToken"]
        with open (credential_file, "w") as actual_credential_file: json.dump (credential_data, actual_credential_file)
        return credential_data ["access_token"]
    @classmethod
    def _send_request (self, *, endpoint, payload):
        response = requests.post (self.server_address + endpoint, headers = {"Content-Type": "application/json"}, json = payload)
        return response.status_code, response.json () if response.status_code != 204 else None
