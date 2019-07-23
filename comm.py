import base64
import ConfigParser
import hashlib
import math
import os
import random
import string

current_path = os.path.dirname(os.path.abspath(__file__))

config = ConfigParser.RawConfigParser(allow_no_value=False)
config.optionxform = str
config.read(os.path.join(current_path, 'config'))
try:
    section = config.sections()[0]
    op_dic = config._sections[section]
except:
    op_dic = {}

WORKSPACE = os.path.join(current_path, op_dic.get('WORKSPACE', 'workspace'))
PORT = op_dic.get('PORT', 5000)
INDEX_MSG = 'Generate Short URL'

default_base = string.ascii_letters + string.digits
CODE_BASE = op_dic.get('CODE_BASE', default_base)
CODE_BASE_LEN = len(CODE_BASE)
CODE_LENGTH = int(op_dic.get('CODE_LENGTH', 6))

ERR_MSG_PROTO = '{} is not a regular url,<br> It should start with "http://" or "https://"'
ERR_MSG_HCODE = '{} is not exists'
DEFAULT_MSG = 'Hi There'

SHORT_URL_MSG = 'The short URL is: {}'

PROTOCOL = 'http://'


def get_hash(the_url, length=6, keep=True, keep_seed=0):
    # without check the_url, length, keep data type
    # generate hash based on SHA1 which has very low collisions rate
    m = hashlib.sha1(the_url)
    sha1 = m.digest()
    if keep is True:
        seed = [keep_seed] * length
    else:
        seed = [random.randint(0, 100) for _ in range(length)]

    res = [0] * length
    if len(sha1) < length:
        times = int(math.ceil(length / len(sha1))) - 1
        org_sha1 = sha1
        for i in range(times):
            sha1 += org_sha1
    pre_value = 0
    for i in range(len(sha1)):
        ind = i % length
        pre_value = (pre_value + ord(sha1[i]) + seed[ind] + res[ind]) % CODE_BASE_LEN
        res[ind] = pre_value
    return ''.join([CODE_BASE[v] for v in res])


def verify_collision(hash_code, long_url):
    fp = os.path.join(WORKSPACE, hash_code[0], hash_code)
    based_url = base64.b64encode(long_url)
    if os.path.exists(fp) is False:
        with open(fp, 'w') as fn:
            fn.write(based_url)
    with open(fp, 'r') as fn:
        r = fn.read()
        if r == based_url:
            return True
        else:
            return False


def get_long_url(hash_code):
    fp = os.path.join(WORKSPACE, hash_code[0], hash_code)
    if os.path.exists(fp) is False:
        return None
    else:
        with open(fp, 'r') as fn:
            r = fn.read()
            return base64.b64decode(r)


if __name__ == '__main__':
    # import pdb; pdb.set_trace()
    import sys
    url = sys.argv[1]
    hash_code = get_hash(url, length=10)
    print(hash_code)
    with open(hash_code, 'wb') as fn:
        fn.write(url)
