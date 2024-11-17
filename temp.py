import secrets
jwt_key = secrets.token_hex(32)
print(jwt_key)