# M-Pesa Daraja Credential Tester
# Run from your project folder with: python test_mpesa.py

import base64
import json
import requests
import os, sys
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'liz_web.settings')
import django
django.setup()
from django.conf import settings

consumer_key = settings.MPESA_CONSUMER_KEY
consumer_secret = settings.MPESA_CONSUMER_SECRET
shortcode = settings.MPESA_SHORTCODE
passkey = settings.MPESA_PASSKEY
env = getattr(settings, 'MPESA_ENV', 'sandbox')
base_url = 'https://sandbox.safaricom.co.ke' if env == 'sandbox' else 'https://api.safaricom.co.ke'

print("=" * 60)
print("  DARAJA CREDENTIAL TESTER")
print("=" * 60)
print("Environment:      " + env)
print("Base URL:         " + base_url)
print("Shortcode:        " + shortcode)
print("Consumer Key:     " + consumer_key)
print("Consumer Secret:  " + consumer_secret)
pk_display = passkey[:20] + "..." if len(passkey) > 20 else passkey
print("Passkey:          " + pk_display)

# STEP 1: OAuth
print("")
print("--- STEP 1: OAuth Token ---")
url = base_url + '/oauth/v1/generate?grant_type=client_credentials'
creds = base64.b64encode((consumer_key + ':' + consumer_secret).encode()).decode()
try:
    r = requests.get(url, headers={'Authorization': 'Basic ' + creds}, timeout=30)
    print("HTTP " + str(r.status_code))
    print("Response: " + r.text)
    if r.status_code != 200:
        print("")
        print("FAILED at OAuth. Fix your Consumer Key or Consumer Secret.")
        sys.exit(1)
    token = r.json().get('access_token')
    if not token:
        print("")
        print("No access_token in response!")
        sys.exit(1)
    print("")
    print("Token: " + token[:30] + "...")
except Exception as e:
    print("ERROR: " + str(e))
    sys.exit(1)

# STEP 2: STK Push
print("")
print("--- STEP 2: STK Push ---")
timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
password = base64.b64encode((shortcode + passkey + timestamp).encode()).decode()
stk_url = base_url + '/mpesa/stkpush/v1/processrequest'
payload = {
    'BusinessShortCode': shortcode,
    'Password': password,
    'Timestamp': timestamp,
    'TransactionType': 'CustomerPayBillOnline',
    'Amount': 1,
    'PartyA': '254708374149',
    'PartyB': shortcode,
    'PhoneNumber': '254708374149',
    'CallBackURL': 'https://mydomain.com/callback/',
    'AccountReference': 'Test',
    'TransactionDesc': 'Test',
}
headers = {
    'Authorization': 'Bearer ' + token,
    'Content-Type': 'application/json',
}
print("URL: " + stk_url)
print("Auth: Bearer " + token[:30] + "...")
print("Payload: " + json.dumps(payload, indent=2))

try:
    r = requests.post(stk_url, json=payload, headers=headers, timeout=30)
    print("")
    print("HTTP " + str(r.status_code))
    print("Response: " + r.text)
except Exception as e:
    print("ERROR: " + str(e))

print("")
print("=" * 60)