from flask import Response
from flask import Flask
from flask import request
from flask import redirect
from flask import render_template
import os

from comm import get_hash, get_long_url, verify_collision
from comm import WORKSPACE, PORT, PROTOCOL
from comm import INDEX_MSG
from comm import CODE_BASE, CODE_LENGTH
from comm import DEFAULT_MSG, ERR_MSG_PROTO, ERR_MSG_HCODE, SHORT_URL_MSG

app = Flask(__name__)


@app.route('/gen_short', methods=["POST"])
def gen_short():
    long_url = request.form.get('url', None)
    res = ''
    if long_url is None or (long_url.startswith('http://') is False and long_url.startswith('https://') is False):
        res = ERR_MSG_PROTO.format(long_url)
    else:
        long_url = long_url.encode('utf8')
        keep = True
        for retry in range(len(CODE_BASE)):
            hash_code = get_hash(long_url, length=CODE_LENGTH, keep=keep)
            verify = verify_collision(hash_code, long_url)
            # if collision gen hash with random seed
            if verify is True:
                break
            else:
                keep = False

        res = '{}{}/{}'.format(PROTOCOL, request.host, hash_code)
    return Response(SHORT_URL_MSG.format(res))


@app.route('/<hash_code>', methods=["GET"])
def re_direct(hash_code):
    long_url = get_long_url(hash_code)
    if long_url is None:
        return Response(ERR_MSG_HCODE.format(hash_code))
    else:
        long_url = long_url.decode('utf8')
        return redirect(long_url, code=302)
    return Response(DEFAULT_MSG)


@app.route('/')
def index():
    '''
    import time
    time.sleep(1)
    return get_hash('html')
    '''
    return render_template('index.htm', message=INDEX_MSG)

if __name__ == '__main__':
    for f in CODE_BASE:
        fp = os.path.join(WORKSPACE, f)
        if os.path.exists(fp) is False:
            # create folders should be successed
            os.makedirs(fp)
    app.run(debug=True, threaded=False, port=PORT)
