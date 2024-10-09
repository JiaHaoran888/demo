import secrets
print(secrets.token_hex(16))  # 生成一个 32 字节的密钥（64 个十六进制字符）
app.secret_key = secrets.token_hex(16)