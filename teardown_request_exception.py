import os

from flask import Flask, g, request, after_this_request

app = Flask(__name__)

request_id = 0
raise_exception = False

def my_after_this_request(f):
    if not hasattr(g, 'after_request_callbacks'):
        g.after_request_callbacks = []
    g.after_request_callbacks.append(f)
    return f

@app.after_request
def call_after_request_callbacks(response):
    for callback in getattr(g, 'after_request_callbacks', ()):
        callback(response)
    return response

@app.route('/')
def index():
    global request_id
    request_id += 1

    global raise_exception
    raise_exception = True if request.args.get("e") else False

    descriptor = 'ReqID%d-pid%d' % (request_id, os.getpid())

    @my_after_this_request
    def set_a_cookie(response):
        custom = "Custom"
        response.headers[descriptor+"-"+custom] = str(request_id) + "-" + custom

    @after_this_request
    def set_another_cookie(response):
        builtin = "Built-In"
        response.headers[descriptor+"-"+builtin] = str(request_id) + "-" + builtin
        return response

    return descriptor

@app.teardown_request
def teardown(exception=None):
    global raise_exception

    if exception:
        print exception
    if raise_exception:
        raise Exception("Exception in 'teardown_request'!")

if __name__ == '__main__':
    app.run()
