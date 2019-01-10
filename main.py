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
from flask import Flask, request, render_template
from model.custom_constraints import assembleJSON
from model.detok import detok


translator = load_translate()
# If `entrypoint` is not defined in app.yaml, App Engine will look for an app
# called `app` in `main.py`.
app = Flask(__name__)

'''
def hello():
    """Return a friendly HTTP greeting."""
    return 'Hello World!'
'''

has_init = False

@app.route('/')
def my_form():
    '''
    global has_init
    if not has_init:
        print('Loading model...')
        print('...Finished')
        has_init = True
    '''
    return render_template('form.html')

@app.route('/', methods=['POST'])
def my_form_post():
    text = request.form['text']
    avoid = request.form['avoid']
    include = request.form['include']
    processed_text = assembleJSON('\t'.join([text, avoid, include]))
    print(processed_text)
    return render_template('form.html') + '\n' + detok(read_and_translate(translator, processed_text))

if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=False, threaded=False)
# [END gae_python37_app]
