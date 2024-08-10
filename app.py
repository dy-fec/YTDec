import os
import cv2
import numpy as np
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import yt_dlp as youtube_dl
import uuid
import time
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

app = Flask(__name__)
CORS(app)


def decrypt_file(input_file: str, output_file: str, key_file: str):
    with open(key_file, 'rb') as kf:
        file_content = kf.read()
        nonce = file_content[:8]
        key = file_content[8:]

    cipher = AES.new(key, AES.MODE_CTR, nonce=nonce)

    with open(input_file, 'rb') as ef:
        ciphertext = ef.read()

    plaintext = cipher.decrypt(ciphertext)

    with open(output_file, 'wb') as df:
        df.write(plaintext)


def decrypt_video(video_path, block_size=2):
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print("Error: Could not open video.")
        return None

    ret, frame = cap.read()
    if not ret:
        print("Error: Could not read first frame.")
        return None

    block_size = 1.0 / block_size

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) - 1
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) * block_size)
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) * block_size)
    total_bits = frame_width * frame_height * total_frames
    binary_array = np.zeros(total_bits, dtype=np.uint8)

    index = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        small_frame = cv2.resize(frame, (0, 0), fx=block_size, fy=block_size)
        gray_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2GRAY)
        _, binary_frame = cv2.threshold(gray_frame, 127, 1, cv2.THRESH_BINARY)
        end_index = index + binary_frame.size
        binary_array[index:end_index] = binary_frame.flatten()
        index = end_index

    cap.release()

    byte_data = np.packbits(binary_array[:index])

    return byte_data


def download_youtube_video(url, output_path):
    ydl_opts = {
        'outtmpl': output_path,
        'format': 'bestvideo/best',
        'merge_output_format': 'mp4',
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


def get_youtube_video_description(url):
    with youtube_dl.YoutubeDL() as ydl:
        info_dict = ydl.extract_info(url, download=False)
        return info_dict.get('description').split(':')[0]


def lookup_cache_key(name, description_key):
    name = "cached/keys/" + name + ".bin"
    description_key = "cached/keys/" + description_key + ".bin"
    if os.path.isfile(name):
        print("Cache key found")
        return name
    elif os.path.isfile(description_key):
        print("Description key found")
        return description_key
    return None


@app.route('/decrypt_video', methods=['POST'])
def decrypt_video_endpoint():
    os.system('cls' if os.name == 'nt' else 'clear')
    if 'url' not in request.form:
        return jsonify({"error": "No URL provided"}), 400

    video_url = request.form['url']
    video_path = uuid.uuid4().hex + '.mp4'
    video_id = video_url.split('?v=')[-1]
    # Handle the key.bin file
    if 'key' in request.files:
        print("Got key")
        key_file = request.files['key']
        key_path = "cached/keys/" + video_id + '.bin'
        key_file.save(key_path)
    else:
        key_path = lookup_cache_key(video_id, get_youtube_video_description(video_url))

    try:
        download_youtube_video(video_url, video_path)
    except Exception as e:
        return jsonify({"error": f"Failed to download video: {str(e)}"}), 400
    print(f'Starting decryption...')
    time_start = time.perf_counter()

    decrypted_data = decrypt_video(video_path)

    time_end = time.perf_counter()
    time_duration = time_end - time_start
    print(f'Decryption took {time_duration} seconds')

    if isinstance(decrypted_data, str):
        return jsonify({"error": decrypted_data}), 400

    output_path = 'static/' + uuid.uuid4().hex + '.webm'
    with open(output_path, 'wb') as f:
        f.write(decrypted_data)

    if os.path.exists(video_path):
        os.remove(video_path)
    else:
        print("Could not delete video.")

    if key_path is not None:
        decrypted_output_path = 'static/dec_' + uuid.uuid4().hex + '.webm'
        decrypt_file(output_path, decrypted_output_path, key_path)
        os.remove(output_path)
        return jsonify({"message": "Video decrypted successfully", "output_path": decrypted_output_path})

    return jsonify({"message": "Video decrypted successfully", "output_path": output_path})


@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)


if __name__ == '__main__':
    if not os.path.exists('static'):
        os.makedirs('static')
    if not os.path.exists('cached/keys'):
        os.makedirs('cached/keys')
    app.run(debug=False)
