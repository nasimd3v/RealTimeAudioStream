import os

from flask import *
import sys
import time

from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

import logging

port = 5090

root = logging.getLogger()
root.setLevel(logging.DEBUG)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
root.addHandler(ch)


def get_current_status():
    try:
        with open('static/audio.log', 'r') as log:
            audio = log.read()
    except:
        audio = "audio.mp3"

    time_ = str(round(time.time() * 1000))
    try:
        with open('static/status.log', 'r') as log:
            time_ = log.read()
    except:
        time_ = str(round(time.time() * 1000))

    return [audio, time_]


def return_dict():
    data = get_current_status()
    dict_here = [
        {
            'id': 1,
            'link': f'static/audios/{data[0]}',
            'startAt': data[1],
            'port': port
        },
    ]
    return dict_here


app = Flask(__name__)


def write_new_file(name):
    with open('static/audio.log', 'w') as log:
        log.write(name)
    with open('static/status.log', 'w') as log:
        log.write(str(round(time.time() * 1000)))


@app.route('/')
def show_entries():
    general_Data = {
        'title': 'Music Player'}
    stream_entries = return_dict()
    return render_template('index.html', entries=stream_entries, **general_Data)


@app.route('/admin')
def admin():
    return render_template('admin.html', name=str(round(time.time() * 1000)))


@app.route('/success', methods=['POST'])
def success():
    if request.method == 'POST':
        f = request.files['file']
        f.save(os.path.join("static/audios/", f.filename))
        write_new_file(f.filename)
        return render_template("success.html", name=f.filename)


def get_audio_from_path():
    file = os.listdir("static/audios")
    return file


# Route to stream music
@app.route('/<int:stream_id>')
def streammp3(stream_id):
    def generate():
        data = return_dict()
        count = 1
        for item in data:
            if item['id'] == stream_id:
                song = item['link']
        with open(song, "rb") as fwav:
            data = fwav.read(1024)
            while data:
                yield data
                data = fwav.read(1024)
                logging.debug('Music data fragment : ' + str(count))
                count += 1

    return Response(generate(), mimetype="static/mpeg")


if __name__ == "__main__":
    http_server = HTTPServer(WSGIContainer(app))
    logging.debug("Started Server, Kindly visit http://localhost:" + str(port))
    http_server.listen(port)
    IOLoop.instance().start()
