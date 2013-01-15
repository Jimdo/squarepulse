import json

def extract_message(rawMessage):
    body = json.loads(rawMessage.get_body())
    kv = [e.split('=', 1) for e in body['Message'].splitlines()]
    kv = [(k, v.strip("'")) for k, v in kv]
    message = dict(kv)
    return message