import json, hashlib, base64, hmac
from Crypto.Cipher import DES3


class Transaction:
    def __init__(self, amount, order, url_ok, url_ko, transaction_type='0', currency='840'):
        self.DS_MERCHANT_AMOUNT = str(amount)
        self.DS_MERCHANT_ORDER = str(order)
        self.DS_MERCHANT_TRANSACTIONTYPE = str(transaction_type)
        self.DS_MERCHANT_CURRENCY = str(currency)
        self.DS_MERCHANT_URLOK = url_ok
        self.DS_MERCHANT_URLKO = url_ko


class Commerce:
    def __init__(self, secret_key, fuc, terminal, url):
        self.secret_key = secret_key
        self.fuc = fuc
        self.terminal = terminal
        self.url = url

    def generate_unique_key(self, order):
        """
        Generate a specific key per operation.
        :param order: The Ds_Merchant_Order number
        :return: a specific key for the operation
        """
        # create cipher with decrypted secret key
        decoded_secret_key = base64.standard_b64decode(self.secret_key)
        cipher = DES3.new(decoded_secret_key, DES3.MODE_CBC, IV=b'\0\0\0\0\0\0\0\0')
        # adjust Ds_Merchant_Order size to multiple of 8
        order = order.ljust(16, '\0')
        return cipher.encrypt(order)

    def generate_form(self, transaction):
        """
        Generates Ds_Signature and Ds_MerchantParameters
        :param transaction: the Transaction object
        :return: { Ds_SignatureVersion, Ds_Signature, Ds_MerchantParameters)
        """
        Ds_SignatureVersion = 'HMAC_SHA256_V1'
        parameters = json.dumps({
            'DS_MERCHANT_AMOUNT': transaction.DS_MERCHANT_AMOUNT,
            'DS_MERCHANT_ORDER': transaction.DS_MERCHANT_ORDER,
            'DS_MERCHANT_TRANSACTIONTYPE': transaction.DS_MERCHANT_TRANSACTIONTYPE,
            'DS_MERCHANT_CURRENCY': transaction.DS_MERCHANT_CURRENCY,
            'DS_MERCHANT_URLOK': transaction.DS_MERCHANT_URLOK,
            'DS_MERCHANT_URLKO': transaction.DS_MERCHANT_URLKO,
            'DS_MERCHANT_MERCHANTCODE': self.fuc,
            'DS_MERCHANT_TERMINAL': self.terminal,
            'DS_MERCHANT_MERCHANTURL': self.url
        })
        Ds_MerchantParameters = base64.b64encode(parameters.encode())

        unique_key = self.generate_unique_key(transaction.DS_MERCHANT_ORDER)

        # plain_text = Ds_MerchantParameters + unique_key
        # sha256 = hashlib.sha256(plain_text).digest()
        # Ds_Signature = base64.b64encode(sha256)
        Ds_Signature = base64.b64encode(hmac.new(unique_key, Ds_MerchantParameters, hashlib.sha256).digest())
        return {
            'Ds_SignatureVersion': Ds_SignatureVersion,
            'Ds_MerchantParameters': Ds_MerchantParameters,
            'Ds_Signature': Ds_Signature,
            'Ds_hmac': Ds_hmac
        }
