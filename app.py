########  imports  ##########
import json
import traceback
from time import strftime

import dotenv
from flask import Flask, request, send_file
from rq import Queue

import handler
from generator.library import Library
from handler import *
from worker import conn

dotenv.load_dotenv(dotenv.find_dotenv())
app = Flask(__name__, static_folder='./dist/', static_url_path='')
q = Queue(connection=conn)
song_library = Library()


def get_remote_ip():
    # Refer https://stackoverflow.com/questions/3759981/get-ip-address-of-visitors-using-flask-for-python
    # Dont forget to change nginx config to support these env variables. You can use any of these
    # print(request.headers.getlist("X-Forwarded-For"))
    # print(request.environ.get('HTTP_X_FORWARDED_FOR'))

    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        return request.environ['REMOTE_ADDR']

    return request.environ.get('HTTP_X_FORWARDED_FOR')


def get_user_id(data):
    userId = data.get('email')
    if not userId:
        userId = get_remote_ip()
    return userId


@app.route('/', methods=['POST', 'GET'])
def gen_hello():
    global song_library
    res = ""
    dist_dir = './dist'
    entry = os.path.join(dist_dir, 'index.html')
    song_library.load_metadata()
    # Create a new user library
    result = create_library.delay(get_remote_ip())
    result.get()
    return send_file(entry)


@app.route('/newSession', methods=['POST'])
def new_session():
    global song_library
    song_library.load_metadata()
    data = request.json
    print("new session:", data.get('email'))

    user_id = get_user_id(request.json)
    result = create_library.delay(user_id)
    result.get()
    res = app.response_class(response=json.dumps({"task_result": 0}),
                             status=200,
                             mimetype="application/json")
    return res


@app.route("/generate", methods=['POST', 'GET'])
def run_task():
    if request.method == "POST":
        data = request.json
        user_id = get_user_id(data)
        task = create_task.delay(data, user_id)

        res = app.response_class(response=json.dumps({"task_id": task.id}),
                                 status=202,
                                 mimetype="application/json")
        return res


@app.route("/requestSpotify", methods=['POST', 'GET'])
def get_track():
    if request.method == "POST":
        data = request.json
        userId = get_user_id(data)

        data = data["url"]
        data = data.split('/')[-1]
        task = add_track.delay(data, userId)

        res = app.response_class(response=json.dumps({"task_id": task.id}),
                                 status=200,
                                 mimetype="application/json")

        return res


@app.route("/addSong", methods=['POST'])
def add_song():
    if request.method == "POST":
        data = request.json
        userId = get_user_id(data)

        task = add_track.delay(data["url"], userId)

        res = app.response_class(response=json.dumps({"task_id": task.id}),
                                 status=200,
                                 mimetype="application/json")

        return res


@app.route("/removeSong", methods=['POST'])
def remove_song():
    if request.method == "POST":
        data = request.json
        userId = get_user_id(data)

        task = remove_track.delay(data["url"], userId)

        res = app.response_class(response=json.dumps({"task_id": task.id}),
                                 status=200,
                                 mimetype="application/json")

        return res


@app.route("/requestTrackList", methods=['POST', 'GET'])
def send_json():
    global song_library
    if request.method == "POST":
        metadata = song_library.get_metadata()
        return metadata


@app.route("/requestStatus/<task_id>", methods=['GET'])
def get_status(task_id):
    print(f"request status: {task_id}")
    task = AsyncResult(task_id, app=celery_app)
    while task.status == "PENDING":
        task = AsyncResult(task_id, app=celery_app)
        # time.sleep(0.1)

    result = {
        "task_id": task_id,
        "requestStatus": task.status,
        "task_result": task.result
    }

    res = app.response_class(response=json.dumps(result),
                             status=200,
                             mimetype="application/json")
    return res


@app.route("/requestResult/<task_id>", methods=['GET'])
def get_result(task_id):
    task_result = AsyncResult(task_id, app=celery_app)
    result = {"task_result": task_result.result}
    res = app.response_class(response=json.dumps(result),
                             status=200,
                             mimetype="application/json")
    return res


@app.route("/requestRegion/<region_id>", methods=['GET'])
def request_region(region_id):
    region = handler.request_region(region_id=region_id)
    return app.response_class(response=json.dumps(region),
                              status=200,
                              mimetype="application/json")


@app.after_request
def after_request(response):
    timestamp = strftime('[%Y-%b-%d %H:%M]')
    logger.error('%s %s %s %s %s %s', timestamp, request.remote_addr, request.method, request.scheme, request.full_path,
                 response.status)
    return response


@app.errorhandler(Exception)
def exceptions(e):
    tb = traceback.format_exc()
    timestamp = strftime('[%Y-%b-%d %H:%M]')
    logger.error('%s %s %s %s %s 5xx INTERNAL SERVER ERROR\n%s', timestamp, request.remote_addr, request.method,
                 request.scheme, request.full_path, tb)
    return e.status_code


#############################
# Launch the server
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    app.run(host='127.0.0.1', port=port)
