import requests
import json
from Crypto.Cipher import AES
import hashlib
import base64
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Util.Padding import pad, unpad

# Request body data
data = {
    "u": "user1",
    "gi": "sharp_arrow_chicken_shoot",
    "dt": 1,
    "st": 12324432424324,
    "s": {"a": "e6be4c2b8b261d576e5e4949027dcf44", "b": "b", "c": "c"},
    "pw": "84660e12cefd5756fb84d996db570c84a1a09f01",
    "m": [
        {
            "sq": 1,
            "m": "session_start",
            "t": 121314232,
            "v": {
                "ga_session_id": 1686298318,
                "engaged_session_event": 1
            }
        },
        {
            "sq": 2,
            "m": "alooo",
            "t": 131415161,
            "v": {
                "session_engaged": 1,
                "ga_session_id": 1686298318,
                "engaged_session_event": 1
            }
        },
        {
            "sq": 2,  # Duplicate s number
            "m": "duplicate_event",
            "t": 1415161718,
            "v": {
                "session_engaged": 1,
                "ga_session_id": 1686298318,
                "engaged_session_event": 1
            }
        },
        {
            "sq": 3,
            "m": "example_event",
            "t": 1415161718,
            "v": {
                "session_engaged": 1,
                "ga_session_id": 1686298318,
                "engaged_session_event": 1
            }
        },
        {
            "sq": 3,  # Duplicate s number
            "m": "another_event",
            "t": 1415161718,
            "v": {
                "session_engaged": 1,
                "ga_session_id": 1686298318,
                "engaged_session_event": 1
            }
        },
        {
            "sq": 4,
            "m": "new_event",
            "t": 1516171819,
            "v": {
                "session_engaged": 1,
                "ga_session_id": 1686298318,
                "engaged_session_event": 1
            }
        },
        {
            "sq": 7,  # Missing s number
            "m": "missing_event",
            "t": 1617181920,
            "v": {
                "session_engaged": 1,
                "ga_session_id": 1686298318,
                "engaged_session_event": 1
            }
        }
    ]
}
data = {"cmd":"lg","u":"0612e50789ce889d103d644e22f8cddc1689247341143","m":"vau9rblnGnOmZAAGr2QNp6kFaxORvbqqom2tOQbASxgOZ2aKEfxWKxsO0VlvGRTD8P7cYXZeHbVMPmcQo+pGKEOf4LSi+j2pll1EfhY+PIr3AZaTfaAX2IhXXQoEVgADIoIZQrHuiLItgj3RlJostQ==","cv":202306090,"pw":"84660e12cefd5756fb84d996db570c84a1a09f01","dt":1,"st":1689355548648,"ut":0,"ud":2.52E+07,"cs":1,"bs":0,"s":{"a":"e6be4c2b8b261d576e5e4949027dcf44","b":"2095131e0e9f05482f644d41fbc39ede","c":"2da5a3001ee61b3bbfbdc9d4f5fbcc5b"},"gi":"sharp_arrow_chicken_shoot","chs":0}

salt = bytes([18, 169, 83, 22, 135, 111, 7, 220, 148, 128, 192, 223, 75, 56, 29, 112, 171])
ciphers = {}
iv = bytes([38, 40, 181, 21, 130, 224, 94, 10, 116, 81, 133, 220, 226, 249, 38, 193])


def create_key(p):
    iterations = 1024
    key = PBKDF2(p, salt, dkLen=16, count=iterations)
    return key

def encrypt(plain_text, p):
    cipher = AES.new(create_key(p), AES.MODE_CBC, iv)
    b = plain_text.encode('utf-8')
    padded_data = pad(b, AES.block_size)
    ctext = cipher.encrypt(padded_data)
    return ctext



# Create AES encryption key
# key = data["p"] + data["s"]["sa"] + data["s"]["sb"] + data["s"]["sc"]
# key = data["pw"] + data["s"]["a"] + data["s"]["b"] + data["s"]["c"]
# p = hashlib.md5(key.encode('utf-8')).hexdigest()
# # encode m to encrypt with AES
# plaintext = json.dumps(data['m'])
# cipher_text = encrypt(plaintext, p)
#
# data["m"] = base64.b64encode(cipher_text).decode()

# Convert data to JSON string
json_data = json.dumps(data)
print(json_data)
# Set the request headers (if required)
headers = {"Content-Type": "application/json"}

# Send the POST request
response = requests.post("http://34.133.113.204:4535/events", data=json_data, headers=headers)

# Check the response status code
if response.status_code == 200:
    # Request was successful
    print("Request successful!")
    print("Response:", response.json())
else:
    # Request failed
    print("Request failed with status code:", response.status_code)
    print("Response:", response.text)
