import requests
import sys

class CookieManager:
    """
    ## You should use "cookies".
    """

    def __init__(self):
            self.cookie = None

    def setCookie(self, cookie:str):
        self.cookie = cookie.replace(".ROBLOSECURITY=", "")
        
        response = requests.get("https://users.roblox.com/v1/users/authenticated",
            headers={
                "Cookie": self.getCookie()
            }
        )

        if response.status_code == 200:
            print(f"logged in as {response.json()["name"]}, {response.json()["id"]}", flush=True)
        else:
            print(f"Error verifying cookie, some functions may not work properly.\nStatus code: {response.status_code}\n{response.text}", file=sys.stderr)

    def getCookie(self) -> str:
        return ".ROBLOSECURITY=" + self.cookie
    
cookies = CookieManager()