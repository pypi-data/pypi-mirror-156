################################################################################
# send zulip messages
################################################################################
import requests
import requests.auth
from time import sleep

# https://zulip.com/api/send-message#send-a-message
def send_zulip(site, email, key, recipient, msg, **kw):
    """Send messages to zulip.

    When recipient is a list, send a private message.  Otherwise the
    recipient should be a "stream[:topic]" string, and a stream message
    is sent.

Optional keyword arguments:
    timeout  --- timeout seconds, default 5
    retry    --- retry times, default 3
    """

    if not recipient:
        raise ValueError('invalid recipient')
    if not msg:
        raise ValueError('invalid msg')

    timeout = kw.get('timeout', 5)
    retries = kw.get('retry', 3)

    request = {'content': msg}
    if isinstance(recipient, list):
        request['type'] = 'private'
        request['to']   = recipient
    elif not isinstance(recipient, str):
        raise TypeError('recipient is not a string')
    else:
        request['type'] = 'stream'
        seg = recipient.split(':')
        if len(seg) > 1:
            request['to']    = ':'.join(seg[:-1])
            request['topic'] = seg[-1]
        else:
            request['to']    = recipient
            request['topic'] = 'bot'

    url = site + '/api/v1/messages'
    session = requests.Session()
    session.auth = requests.auth.HTTPBasicAuth(email, key)
    session.verify = True
    session.headers.update({"User-agent": "wei (Linux; 5.4.0-100-generic)"})
    while True:
        try:
            rsp = session.request('POST', url, timeout=timeout, data=request)
            good = rsp.status_code == 200
        except:
            good = False
        if good or not retries:
            break
        sleep(1)
        retries -= 1

### wei/zulip.py ends here
