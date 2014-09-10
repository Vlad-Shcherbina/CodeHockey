import sys
sys.path.append('../strategy')

import glob
import os
import re

import flask
import jinja2

import recorder

app = flask.Flask(__name__)

template_loader = jinja2.FileSystemLoader('templates')
app.jinja_loader = template_loader


# Custom static data
@app.route('/replay_data/<path:filename>')
def custom_static(filename):
    res = flask.send_from_directory(recorder.REPLAY_DIR, filename)
    print(res)
    return res


@app.route('/')
def index():
    frames = set()
    files = glob.glob(os.path.join(recorder.REPLAY_DIR, '*'))
    for filename in files:
        base, ext = os.path.splitext(os.path.basename(filename))
        m = re.match(r'[a-z_]*(\d+)$', base)
        frames.add(m.group(1))
    frames = sorted(frames)

    return flask.render_template('main.html', **locals())


def main():
    app.debug = True
    app.run()


if __name__ == '__main__':
    main()
