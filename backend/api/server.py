import os
import sys
from flask import Flask
from flask import request, make_response, jsonify, send_file
from flask_cors import CORS

app = Flask(__name__, static_folder='', template_folder='')
CORS(app)

import cv2
import numpy as np

# Logging
import logging
logger = logging.getLogger(os.path.basename(__file__))
logger.setLevel(logging.INFO)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
handler_format = logging.Formatter('%(asctime)s : [%(name)s - %(lineno)d] %(levelname)-8s - %(message)s')
stream_handler.setFormatter(handler_format)
logger.addHandler(stream_handler)

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../src/')
from timecode_coincident import TimeCodeCoincident
from get_frams_diff import GetFramesDiff

coincidenter = TimeCodeCoincident()
diff_parser = GetFramesDiff()

def axios_video_to_videocapture(video_file, temp_filename='temp_video.mp4'):
  # Convert the uploaded file to a cv2 video capture
  video_stream = video_file.stream
  video_array = np.frombuffer(video_stream.read(), dtype=np.uint8)

  # Create a temporary file and write the video data
  with open(temp_filename, 'wb') as temp_file:
    temp_file.write(video_array.tobytes())

  # Use cv2.VideoCapture with the temporary file
  video_capture = cv2.VideoCapture(temp_filename)

  return video_capture

@app.route('/', methods=['GET'])
def index():
  return 'Flask server is running :)'

@app.route('/set_source_name', methods=['POST'])
def set_source_name():
  arguments = request.get_json()
  coincidenter.set_source_name(source_name=arguments['source_name'])
  diff_parser.set_source_name(source_name=arguments['source_name'])
  response = {'result': True}

  return make_response(jsonify(response))

@app.route('/set_target_name', methods=['POST'])
def set_target_name():
  arguments = request.get_json()
  coincidenter.set_target_name(target_name=arguments['target_name'])
  diff_parser.set_target_name(target_name=arguments['target_name'])
  response = {'result': True}

  return make_response(jsonify(response))

@app.route('/set_source_video', methods=['POST'])
def set_source_video():
  source_video = axios_video_to_videocapture(
    video_file=request.files['video'],
    temp_filename='temp_source_video.mp4',
  )
  coincidenter.set_source_video(source_video=source_video)
  diff_parser.set_source_video(source_video=source_video)
  response = {'result': True}

  return make_response(jsonify(response))

@app.route('/set_target_video', methods=['POST'])
def set_target_video():
  target_video = axios_video_to_videocapture(
    video_file=request.files['video'],
    temp_filename='temp_target_video.mp4',
  )
  coincidenter.set_target_video(target_video=target_video)
  diff_parser.set_target_video(target_video=target_video)
  response = {'result': True}

  return make_response(jsonify(response))

@app.route('/set_config/<config>', methods=['GET'])
def set_config(config: str):
  coincidenter.set_config(config=config)
  response = {'result': True}

  return make_response(jsonify(response))

@app.route('/get_video_information/<videokind>', methods=['GET'])
def get_video_information(videokind: str):
  information = coincidenter.get_video_information(videokind=videokind)
  response = {'result': True, 'information': information}

  return make_response(jsonify(response))

@app.route('/execute', methods=['GET'])
def execute():
  list_source_frame_ids = coincidenter.execute()
  response = {'result': True, 'list_source_frame_ids': list_source_frame_ids}

  return make_response(jsonify(response))

@app.route('/generate_output_file', methods=['POST'])
def generate_output_file():
  arguments = request.get_json()
  str = coincidenter.generate_output_file(as_str=arguments['as_str'])
  response = {'result': True, 'str': str}

  return make_response(jsonify(response))

@app.route('/get_generated_output_file', methods=['GET'])
def get_generated_output_file():
  filepath = coincidenter.get_output_file_name()
  filename = os.path.basename(filepath)

  return send_file(filepath, as_attachment=True, download_name=filename, mimetype='text/plain')

@app.route('/get_frames_diff', methods=['POST'])
def get_frames_diff():
  arguments = request.get_json()
  b64_frame = diff_parser.generate_diff_image(
    source_iframe=arguments['sourceFrameID'],
    target_iframe=arguments['targetFrameID'],
    as_b64=True,
  )
  response = {'result': True, 'b64_frame': b64_frame}

  return make_response(jsonify(response))

if __name__ == '__main__':
  app.debug = True
  app.run(host='127.0.0.1', port=5432)