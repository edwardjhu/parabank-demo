# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START gae_python37_app]
import sys
import os
from sockeye_wrapper import *
from flask import Flask, request, render_template, jsonify
import logging
from model_NAACL19.custom_constraints import assembleJSON
from model_NAACL19.detok import detok


translator = load_translate('model_NAACL19')
# If `entrypoint` is not defined in app.yaml, App Engine will look for an app
# called `app` in `main.py`.
app = Flask(__name__)

'''
def hello():
    """Return a friendly HTTP greeting."""
    return 'Hello World!'
'''

has_init = False
line =  '<hr style="border: 2px solid black;" />'
@app.route('/')
def my_form():
    '''
    global has_init
    if not has_init:
        print('Loading model...')
        print('...Finished')
        has_init = True
    '''
    return render_template('form.html', text="The quick fox jumped over the lazy dog.", avoid='quick fox|dog', include='leaped', nbest=5)

@app.route('/', methods=['POST'])
def my_form_post():
    text = request.form['text']
    avoid = request.form['avoid']
    include = request.form['include']
    nbest_size = int(request.form['nbest'])
    processed_text = assembleJSON('\t'.join([text, avoid, include]))
    result_list = read_and_translate(translator, processed_text, nbest_size=nbest_size)
    for i in range(len(result_list)):
        result_list[i] = detok(result_list[i])
    print('LOG', str({'request': processed_text, 'IP': request.environ['REMOTE_ADDR'], 'output': result_list}))
    return render_template('form.html', text=text, avoid=avoid, include=include, nbest=nbest_size) + line \
            + text + '<br>' + '<b>' + '<br>'.join(result_list) + '</b>'

if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=False, threaded=False)
# [END gae_python37_app]
