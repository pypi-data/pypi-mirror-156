from socket import gethostname
from getpass import getuser

def signature(sep = None):
    sig = f"{getuser()}@{gethostname()}"
    if sep:
        return '\n\n%s\n%s\n' % (sep * len(sig), sig)
    return sig
