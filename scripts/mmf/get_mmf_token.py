"""
One-time OAuth2 helper: open browser, you log in to MyMiniFactory, we capture the
redirect and exchange the code for an access token. Then use that token as MMF_API_KEY
in fetch_mmf_library.py (or set env MMF_API_KEY).

Prerequisites:
  1. Create an app at https://www.myminifactory.com/settings/developer/application
  2. Add this redirect URI to your app:  http://localhost:8765/callback
  3. Set MMF_CLIENT_ID and MMF_CLIENT_SECRET below (or in env).
"""

import os
import random
import string
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

try:
    import requests
except ImportError:
    print("Install requests: pip install requests")
    exit(1)

# --- Edit or set in env ---
# From MMF: https://www.myminifactory.com/settings/developer/application
#   - "Client key" on MMF = use as MMF_CLIENT_ID (e.g. Ov23liArW0jSKx0WT2GS)
#   - You also need a Client secret (may be "Secret" or "Show secret" on the same app page)
#   - Redirect URI in app must be: http://localhost:8765/callback
MMF_CLIENT_ID = os.environ.get("MMF_CLIENT_ID", "Ov23liArW0jSKx0WT2GS")
MMF_CLIENT_SECRET = os.environ.get("MMF_CLIENT_SECRET", "pONj2GQIWPK0hr6jpfzjRtMyX4CvwT")
REDIRECT_URI = "http://localhost:8765/callback"
AUTH_URL = "https://auth.myminifactory.com/web/authorize"
TOKEN_URL = "https://auth.myminifactory.com/v1/oauth/tokens"

# Server will set this when redirect is received
auth_code = None
state_expected = None


class CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global auth_code
        parsed = urlparse(self.path)
        if parsed.path == "/callback" or parsed.path == "/":
            q = parse_qs(parsed.query)
            if "code" in q:
                auth_code = q["code"][0]
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(
                    b"<h1>Success</h1><p>You can close this tab and return to the terminal.</p>"
                )
            elif "error" in q:
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(
                    f"<h1>Denied</h1><p>Error: {q.get('error', [''])[0]}</p>".encode()
                )
            else:
                self.send_response(400)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass


def main():
    global state_expected
    if MMF_CLIENT_ID in ("", "YOUR_CLIENT_ID") or MMF_CLIENT_SECRET in ("", "YOUR_CLIENT_SECRET"):
        print("Set MMF_CLIENT_ID and MMF_CLIENT_SECRET at the top of this script (or in env).")
        print("Get them from https://www.myminifactory.com/settings/developer/application")
        print("Add redirect URI: http://localhost:8765/callback")
        return

    state_expected = "".join(random.choices(string.ascii_letters + string.digits, k=16))
    auth_link = (
        f"{AUTH_URL}?client_id={MMF_CLIENT_ID}&redirect_uri={REDIRECT_URI}"
        f"&response_type=code&state={state_expected}"
    )

    print("Opening browser for MyMiniFactory login...")
    print("If nothing opens, go to:")
    print(auth_link)
    webbrowser.open(auth_link)

    server = HTTPServer(("localhost", 8765), CallbackHandler)
    server.handle_request()
    server.server_close()

    if not auth_code:
        print("No authorization code received. Check that redirect URI is http://localhost:8765/callback in your app.")
        return

    def exchange(code, client_id, client_secret):
        return requests.post(
            TOKEN_URL,
            auth=(client_id, client_secret),
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": REDIRECT_URI,
            },
            timeout=30,
        )

    print("Exchanging code for access token...")
    r = exchange(auth_code, MMF_CLIENT_ID, MMF_CLIENT_SECRET)

    # If 401 and MMF only shows "Client key" (no separate secret), try using Client key as both id and secret
    if not r.ok and r.status_code == 401 and MMF_CLIENT_SECRET != MMF_CLIENT_ID:
        print("Retrying with Client key as secret (in case MMF only provides one value)...")
        r = exchange(auth_code, MMF_CLIENT_ID, MMF_CLIENT_ID)

    if not r.ok:
        try:
            err = r.json()
        except Exception:
            err = r.text
        print(f"Token exchange failed ({r.status_code}): {err}")
        if r.status_code == 401 and "client" in str(err).lower():
            print()
            print("Invalid client ID or secret — try:")
            print("  1. Open https://www.myminifactory.com/settings/developer/application")
            print("  2. MMF shows 'Client key' = use as MMF_CLIENT_ID. You also need a Client secret.")
            print("  3. Look for 'Client secret', 'Secret', or 'Regenerate' / 'Show secret' on the same app.")
            print("  4. Re-copy both (no spaces). If you regenerated the secret, use the current one.")
            print("  5. Or use session cookie instead: $env:MMF_SESSION_COOKIE = \"...\"; see docs/MMF-Fetcher-Setup.md")
        else:
            print("Check that client ID and secret are correct and redirect URI is exactly http://localhost:8765/callback in your app.")
        return
    data = r.json()
    token = data.get("access_token")
    refresh = data.get("refresh_token")
    expires = data.get("expires_in", 0)

    if not token:
        print("Response:", data)
        return

    print()
    print("Success. Use this as MMF_API_KEY in fetch_mmf_library.py (line 38) or set env:")
    print()
    print(f"  MMF_API_KEY={token}")
    print()
    print(f"  (Expires in {expires} seconds; use refresh_token to get a new one if needed.)")
    if refresh:
        print(f"  Refresh token (save for later): {refresh[:20]}...")


if __name__ == "__main__":
    main()
