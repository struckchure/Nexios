import base64
import json
import hmac
import hashlib

class SessionEncoder:
    def __init__(self, secret_key: str):
        self.secret_key = secret_key

    def encode_session(self, session_data: dict) -> str:
        # Encode the session data as a JSON string
        json_data = json.dumps(session_data)
        # Base64 encode the JSON string
        data = base64.b64encode(json_data.encode()).decode()
        # Create a signature for the encoded data
        signature = hmac.new(self.secret_key.encode(), data.encode(), hashlib.sha256).hexdigest()
        
        # Return the encoded data and the signature joined by a period
        return f"{data}.{signature}"

    def decode_session(self, encoded_data: str) -> dict:
        # Split the encoded data into data and signature parts
        data, signature = encoded_data.rsplit('.', 1)
        
        # Recompute the expected signature
        expected_signature = hmac.new(self.secret_key.encode(), data.encode(), hashlib.sha256).hexdigest()
        
        # Verify that the signature matches
        if not hmac.compare_digest(expected_signature, signature):
            raise ValueError("Invalid session data or tampering detected")
        
        # Decode the JSON data from base64
        json_data = base64.b64decode(data.encode()).decode()
        # Return the decoded JSON as a dictionary
        return json.loads(json_data)
