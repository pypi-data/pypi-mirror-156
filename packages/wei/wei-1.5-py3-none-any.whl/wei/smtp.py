import os, smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
from email.encoders import encode_base64
from wei import signature

def send_mail(acc, recipients, subject, text, **kw):
    """
    Optional keyword arguments:
    username --- username used in SMTP login
    addr     --- sender email address
    html     --- send HTML or not
    files    --- file attatchments
    cc       --- Cc address list
    """
    segs = acc.split(':')
    if len(segs) == 2:
        user = segs[0]
        passwd, host = segs[1].split('@')
        port = None
    elif len(segs) == 3:
        user = segs[0]
        passwd, host = segs[1].split('@')
        port = int(segs[2])

    if isinstance(recipients, str):
        recipients = [recipients]

    smtpuser = kw.get('username', user)
    addr = kw.get('addr', user)
    html = bool(kw.get('html', False))
    files = kw.get('files', None)
    cc = kw.get('cc', None)

    sig = kw.get('signature', True) and signature('-') or ''
    txtmsg = MIMEText(text + sig, html and 'html' or 'plain', 'UTF-8')

    # construct whole message
    if files:
        msg = MIMEMultipart()
        msg.attach(txtmsg)
        for fname in files:
            part = MIMEBase('application', "octet-stream")
            with open(fname, 'rb') as fh:
                part.set_payload(fh.read())
            encode_base64(part)
            part.add_header('Content-Disposition', 'attachment; filename="%s"'
                            % os.path.basename(fname))
            msg.attach(part)
    else:
        msg = txtmsg

    msg['From'] = addr
    msg['To'] = COMMASPACE.join(recipients)
    if cc:
        msg['Cc'] = COMMASPACE.join(cc)
        recipients += cc
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject

    # send out message
    if port is None or port in [25, 587]:
        smtp = smtplib.SMTP(host, port, timeout=5)
        if port == 587:
            smtp.starttls()
    else:
        smtp = smtplib.SMTP_SSL(host, port, timeout=5)
    smtp.login(user, passwd)
    smtp.sendmail(smtpuser, recipients, msg.as_string())
    smtp.close()

### wei/smtp.py ends here
