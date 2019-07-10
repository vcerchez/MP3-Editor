# MP3-Editor
MP3-Editor is a wrapper around FFmpeg (https://ffmpeg.org/) command-line multimedia editor. It uses Python to build a GUI that simplifies the use of FFmpeg native command-line interface.

The editor is supposed to be used with audio files containing audio books and lectures without any particular attention to the quality of the produced MP3 files (the only quality concern is the size of the output files). Thus it **should not be used to edit _music files_ or any other files where the audio quality is of prime concern**.

The editor was built and tested in Windows 10 environment while it should be easily transferable to Linux and MacOS environments.

## Functionality
Currently the editor can process MP4 and MP3 files.

In the case of video MP4 files the audio track is extracted and converted to MP3.

The editor allows one to adjust (increase) the volume level of the audio files, their (average) bitrate, as well as to edit some of the MP3 tags such as the artist name, the album name, the title of the track and the track number.

Once the changes are commited, the MP3 file is processed and saved in the folder chosen by user.

Example of MP3 Editor's GUI:

![GUI example](MP3-Editor-GUI-example.png)

## Installation and dependences
Properly installed (PATH) FFmpeg is primerely required for the program to function. The latest version of FFmpeg can be downloaded from the program's home page https://ffmpeg.org/download.html#build-windows.

After installation the FFmpeg must be aded to Windows PATH environment. This can be done e.g. as follows:
Navigate to Advanced System Information window (Start Menu -> Parameters -> System -> Information about the System -> System information -> Advanced parameters)...

The program itself can be used either as a Python script or as a precompiled exe file. To run the script Python v.3.7.3 or newer is required, with wxPython GUI module (https://wxpython.org/) v.4.0.4 or newer. For the use of precompiled exe file no other requirement than installed FFmpeg is needed.
