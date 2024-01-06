import hmac
import hashlib
import base64

data = '123'
secret = '234'

digest = hmac.new(secret.encode('utf-8'), data, digestmod=hashlib.sha256).digest()
computed_hmac = base64.b64encode(digest)

print (computed_hmac)
