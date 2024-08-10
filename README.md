# YTDec a fast video decryptor
A tool for encryption and decryption of YT-Videos, inspired by [DvorakDwarf/Infinite-Storage-Glitch](https://github.com/DvorakDwarf/Infinite-Storage-Glitch).
YTDec downloads, decrypts and replaces the video on Youtube, using an AES-key is optional.
Currently the decryption is pretty fast, the encryption is a bit slow.


# Features
  - Encrpytion of videos
  - Fast decryption of videos 
  - Replacing the decrypted video on YT
  - Allowing to AES-encryption of the Video (optional)
    - Only persons that have the key can watch the video
    - shared key in description for ease of use
    - NO AI is trained on your voice or video
      
# How-to
Git clone the repo
```
git clone https://github.com/dy-fec/YTDec.git
```
and run "start.bat"
## Encryption of videos

Activate the venv created with "start.bat".

Encrpytion of an video without using an key:
```
python .\encrypt.py video.mp4 videonoenc.mp4
```
The encrypted video is saved and can be uploaded onto YT


Encryption using an key:

If a keyfile is provided that allready exists its reused, otherwise a new keyfile is created.
The video cant be decrypted if you lose the key!
```
python .\encrypt.py video.mp4 videoenc.mp4 --key_file new.bin
```

The keyfile can be saved or provided to persons that are allowed to watch the video.

For ease of use the description can be used to specify a key that is in /cached/keys

<img width="638" alt="Screenshot 2024-08-10 190011" src="https://github.com/user-attachments/assets/2b270c59-e633-44d3-a5e6-ab742a10535e">

The word before the : is extraced to allow channel wide encryption and decryption with providing only one key.
Text after the : can be anything you want. Discord, Patreon etc.
In this example the key that would be looked up would be under /cached/keys/mydescription.bin


## Decription
1. Start the server with "start.bat"
2. Create a bookmark with the URL containing the JS provided in this repo under "bookmark.txt"
![Screenshot 2024-08-10 185641](https://github.com/user-attachments/assets/faada495-1430-44cb-919d-f4c38e4eed77)
3. Open an encrypted video
4. If needed you can provide an key
   Each key is stored in /cached/keys/ with the yt-url for reuse
   If the description contains a keyname this key is searched for in  /cached/keys/
![Screenshot 2024-08-10 185721](https://github.com/user-attachments/assets/be01e8a5-157d-4a53-8c5d-d0112cab8d64)
5. The video is downloaded decrypted, and replaces the original video on YT
<img width="1159" alt="Screenshot 2024-08-10 185846" src="https://github.com/user-attachments/assets/02f9e64c-bfbe-4ae2-a0fa-9204f490f890">

# Why
Today videos are scrapped by bots and used to train AIs without the permission of the user.
Even without using an AES-key for extra encryption, the decryption takes alot of compute (so its pretty unlikely that they end up in AI-trainingdata).
The "new"-Youtube is an toxic pile of censorship, media, hate and clickbait.
With using an AES-key its pretty much a private video you can share.
