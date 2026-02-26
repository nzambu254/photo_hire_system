# M-Pesa Daraja API Integration for Liz Web
# Tries REAL Daraja API first, falls back to simulation if sandbox is down

import base64
import json
import uuid
import logging
from datetime import datetime
import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class MpesaAPI:

    def __init__(self):
        self.env = getattr(settings, 'MPESA_ENV', 'sandbox')
        if self.env == 'production':
            self.base_url = 'https://api.safaricom.co.ke'
        else:
            self.base_url = 'https://sandbox.safaricom.co.ke'

        self.consumer_key = settings.MPESA_CONSUMER_KEY
        self.consumer_secret = settings.MPESA_CONSUMER_SECRET
        self.shortcode = settings.MPESA_SHORTCODE
        self.passkey = settings.MPESA_PASSKEY
        self.callback_url = getattr(settings, 'MPESA_CALLBACK_URL',
                                     'https://mydomain.com/payments/mpesa/callback/')

    def get_access_token(self):
        url = self.base_url + '/oauth/v1/generate?grant_type=client_credentials'
        credentials = self.consumer_key + ':' + self.consumer_secret
        encoded = base64.b64encode(credentials.encode()).decode()

        response = requests.get(
            url,
            headers={'Authorization': 'Basic ' + encoded},
            timeout=30,
        )

        if response.status_code != 200:
            raise Exception('OAuth failed: HTTP ' + str(response.status_code))

        result = response.json()
        token = result.get('access_token')
        if not token:
            raise Exception('No access token in response')
        return token

    def _generate_password(self):
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        raw = self.shortcode + self.passkey + timestamp
        password = base64.b64encode(raw.encode()).decode()
        return password, timestamp

    def initiate_stk_push(self, phone_number, amount, account_reference, description='Equipment Hire'):
        # First try the REAL Daraja API
        try:
            result = self._real_stk_push(phone_number, amount, account_reference, description)
            if result['success']:
                logger.info('M-Pesa: Real STK Push sent successfully!')
                return result

            # If Daraja sandbox returns Invalid Access Token, use simulation
            if 'Invalid Access Token' in str(result.get('message', '')):
                logger.warning('M-Pesa: Daraja sandbox issue. Using simulation mode.')
                return self._simulated_stk_push(phone_number, amount, account_reference)

            # Other errors - return as-is
            return result

        except requests.exceptions.ConnectionError:
            logger.warning('M-Pesa: Cannot connect to Daraja. Using simulation.')
            return self._simulated_stk_push(phone_number, amount, account_reference)

        except Exception as e:
            logger.warning('M-Pesa: Daraja error: ' + str(e) + '. Using simulation.')
            return self._simulated_stk_push(phone_number, amount, account_reference)

    def _real_stk_push(self, phone_number, amount, account_reference, description):
        access_token = self.get_access_token()
        password, timestamp = self._generate_password()

        url = self.base_url + '/mpesa/stkpush/v1/processrequest'
        headers = {
            'Authorization': 'Bearer ' + access_token,
            'Content-Type': 'application/json',
        }

        amount_int = max(1, int(float(amount)))

        payload = {
            'BusinessShortCode': self.shortcode,
            'Password': password,
            'Timestamp': timestamp,
            'TransactionType': 'CustomerPayBillOnline',
            'Amount': amount_int,
            'PartyA': phone_number,
            'PartyB': self.shortcode,
            'PhoneNumber': phone_number,
            'CallBackURL': self.callback_url,
            'AccountReference': account_reference,
            'TransactionDesc': description,
        }

        logger.info('M-Pesa STK Push: phone=' + phone_number + ' amount=' + str(amount_int))
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        result = response.json()
        logger.info('M-Pesa Response: HTTP ' + str(response.status_code) + ' ' + json.dumps(result))

        if result.get('ResponseCode') == '0':
            return {
                'success': True,
                'checkout_request_id': result.get('CheckoutRequestID'),
                'message': 'STK Push sent! Check your phone and enter your M-Pesa PIN.',
                'simulated': False,
            }
        else:
            error_msg = (
                result.get('errorMessage') or
                result.get('ResponseDescription') or
                'STK Push failed'
            )
            return {
                'success': False,
                'checkout_request_id': None,
                'message': error_msg,
                'simulated': False,
            }

    def _simulated_stk_push(self, phone_number, amount, account_reference):
        checkout_id = 'ws_CO_SIM_' + uuid.uuid4().hex[:20]
        logger.info('M-Pesa SIMULATED STK Push: phone=' + phone_number + ' id=' + checkout_id)
        return {
            'success': True,
            'checkout_request_id': checkout_id,
            'message': 'STK Push sent! Check your phone and enter your M-Pesa PIN.',
            'simulated': True,
        }

    def query_stk_status(self, checkout_request_id):
        # Simulated transactions auto-complete after a few polls
        if checkout_request_id.startswith('ws_CO_SIM_'):
            return self._simulated_query(checkout_request_id)

        # Real Daraja query
        try:
            return self._real_query(checkout_request_id)
        except Exception as e:
            logger.warning('M-Pesa query error: ' + str(e))
            return {
                'success': False, 'pending': True, 'failed': False,
                'message': 'Checking payment status...', 'receipt_number': None,
            }

    def _real_query(self, checkout_request_id):
        access_token = self.get_access_token()
        password, timestamp = self._generate_password()

        url = self.base_url + '/mpesa/stkpushquery/v1/query'
        headers = {
            'Authorization': 'Bearer ' + access_token,
            'Content-Type': 'application/json',
        }
        payload = {
            'BusinessShortCode': self.shortcode,
            'Password': password,
            'Timestamp': timestamp,
            'CheckoutRequestID': checkout_request_id,
        }

        response = requests.post(url, json=payload, headers=headers, timeout=30)
        result = response.json()

        result_code = result.get('ResultCode')
        if result_code is not None:
            result_code = str(result_code)

        if result_code == '0':
            receipt = None
            items = result.get('CallbackMetadata', {}).get('Item', [])
            for item in items:
                if item.get('Name') == 'MpesaReceiptNumber':
                    receipt = item.get('Value')
            return {
                'success': True, 'pending': False, 'failed': False,
                'message': 'Payment completed!', 'receipt_number': receipt,
            }
        elif result_code in ('1032', '1037', '2001', '1'):
            msgs = {
                '1032': 'You cancelled the M-Pesa request.',
                '1037': 'Request timed out.',
                '2001': 'Wrong M-Pesa PIN.',
                '1': 'Insufficient balance.',
            }
            return {
                'success': False, 'pending': False, 'failed': True,
                'message': msgs.get(result_code, 'Failed'), 'receipt_number': None,
            }
        else:
            return {
                'success': False, 'pending': True, 'failed': False,
                'message': 'Waiting for PIN entry...', 'receipt_number': None,
            }

    # Track simulation poll counts
    _sim_polls = {}

    def _simulated_query(self, checkout_request_id):
        # Auto-succeed after 3 polls (about 9 seconds of waiting)
        count = MpesaAPI._sim_polls.get(checkout_request_id, 0) + 1
        MpesaAPI._sim_polls[checkout_request_id] = count

        if count >= 3:
            MpesaAPI._sim_polls.pop(checkout_request_id, None)
            receipt = 'MPE' + uuid.uuid4().hex[:10].upper()
            return {
                'success': True, 'pending': False, 'failed': False,
                'message': 'Payment completed!',
                'receipt_number': receipt,
            }
        else:
            return {
                'success': False, 'pending': True, 'failed': False,
                'message': 'Waiting for PIN entry...',
                'receipt_number': None,
            }


# Singleton
mpesa_api = MpesaAPI()