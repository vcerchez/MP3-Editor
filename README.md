# MP3-Editor
MP3 Editor is a wrapper around FFmpeg (https://ffmpeg.org/) command-line multimedia editor. It uses Python to build a GUI that simplifies the use of FFmpeg native command-line interface.

The editor was primarely created to be used with audio books and lectures without particular attention to the quality of the output MP3 files (the only quality concern was the size of the files) and **should not be used to edit _music files_ or any other files where the audio quality is of prime concern**.

## Functionality
Currently the editor can process MP4 and MP3 files. In the case of video MP4 files the audio track will be extracted and converted to MP3 one.
Currently the editor allows to adjust (increase) the volume level of the audio files, their (average) bitrate, as well as edit some of the MP3 tags such as artist name, alum name, title of the track and track number.
Once the change are commited, the MP3 files are processed and saved in the folder chosen by user.

## Installation and dependences
Properly installed (PATH) FFmpeg is primerely required for the program to function. How to set FFmpeg to PATH environement is described below.
The program itself can be used either as a Python script or as a precompiled exe file.
In the former case the Python >= 3.7 is required, as well as wxpython >=4.04 gui module are required.
For the use of precompiled exe file no other requirement than installed FFmpeg is needed.

## Setting PATH environment for FFmpeg
How to set PATH
