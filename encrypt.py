import cv2
import numpy as np
import time
import argparse
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import os


def encrypt_file(input_file: str, output_file: str, key_file: str):
    if os.path.isfile(key_file):
        print("Key file exists. Skipping generating key.")
        with open(key_file, 'rb') as kf:
            file_content = kf.read()
            nonce = file_content[:8]  # nonce
            key = file_content[8:]  # key
    else:
        key = get_random_bytes(32)
        nonce = get_random_bytes(8)
        with open(key_file, 'wb') as kf:
            kf.write(nonce + key)
    cipher = AES.new(key, AES.MODE_CTR, nonce=nonce)

    with open(input_file, 'rb') as f:
        plaintext = f.read()
    ciphertext = cipher.encrypt(plaintext)

    with open(output_file, 'wb') as ef:
        ef.write(ciphertext)


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


def encrypt_file_to_video(input_file_path, output_video_path, block_size=4, key_file=None):

    if key_file is not None:
        encrypt_file(input_file_path, "decaes_" + input_file_path, key_file)
        input_file_path = "decaes_" + input_file_path
    with open(input_file_path, 'rb') as f:
        file_data = f.read()
    binary_data = ''.join(format(byte, '08b') for byte in file_data)

    frame_width = 1280 * 3
    frame_height = 720 * 3
    fps = 10
    frame_size = (frame_width, frame_height)

    blocks_per_row = frame_width // block_size
    blocks_per_col = frame_height // block_size

    bits_per_frame = blocks_per_row * blocks_per_col

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_video_path, fourcc, fps, frame_size, isColor=False)
    blank_frame = np.zeros((frame_height, frame_width), np.uint8)
    out.write(blank_frame)

    row_indices, col_indices = np.indices((blocks_per_col, blocks_per_row))
    row_indices = (row_indices * block_size).flatten()
    col_indices = (col_indices * block_size).flatten()

    num_frames = (len(binary_data) + bits_per_frame - 1) // bits_per_frame
    for frame_idx in range(num_frames):
        frame = np.zeros((frame_height, frame_width), np.uint8)
        bit_idx_start = frame_idx * bits_per_frame
        bit_idx_end = min(bit_idx_start + bits_per_frame, len(binary_data))
        bits = np.fromiter(map(int, binary_data[bit_idx_start:bit_idx_end]), dtype=np.uint8)

        rows = row_indices[:len(bits)]
        cols = col_indices[:len(bits)]

        for row, col, bit in zip(rows, cols, bits):
            frame[row:row + block_size, col:col + block_size] = 255 * bit

        out.write(frame)

    out.release()
    print(f"Video saved to {output_video_path}")


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Decrypt video to binary data.")
    parser.add_argument('input_file', help="Path to the input video file.")
    parser.add_argument('output_file', help="Path to the output binary data file.")
    parser.add_argument('--block_size', type=float, default=2.0, help="Block size for processing. Default is 2.")
    parser.add_argument('--key_file', default=None, help="Path to key file")
    args = parser.parse_args()
    output_video_path = args.output_file

    time_start = time.perf_counter()

    ### encryption

    encrypt_file_to_video(args.input_file, output_video_path, int(args.block_size), key_file=args.key_file)

    time_end = time.perf_counter()
    time_duration = time_end - time_start
    print(f'Encryption took {time_duration} seconds')

    ### decryption
    time_start = time.perf_counter()

    decrypted_data = decrypt_video(output_video_path, args.block_size)

    time_end = time.perf_counter()
    time_duration = time_end - time_start
    print(f'Decryption took {time_duration} seconds')
    with open("redec_" + args.output_file, 'wb') as f:
        f.write(decrypted_data)
    if args.key_file is not None:
        decrypt_file("redec_" + args.output_file, "enc_" + "redec_" + args.output_file, "key.bin")
