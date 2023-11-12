import base64


def decode_base64_str(base64_str: str) -> str:
    return base64.b64decode(base64_str.encode("utf-8") + b"==").decode("utf-8")
