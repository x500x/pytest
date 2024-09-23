import os
#import 123uplaod
from uplaod import uploader
#\'\\r\\n\'

Downloadvideo_path="C:\\videos\\"
Downloadvideo_name="Download_video.mp4"
os.system("md C:\\videos")
#os.system("you-get https://b23.tv/CstBqCK -i -c .\\c.txt")
os.system("you-get https://b23.tv/CstBqCK -O 1 -o C:\\videos -c .\\c.txt --debug")
os.system("dir C:\\videos")
os.system(".\\ffmpeg-7.0.2-full_build\\bin\\ffmpeg.exe -i C:\\videos\\1[00].mp4 -i C:\\videos\\1[01].mp4 -c:v copy -c:a copy -f mp4 C:\\videos\\Download_video.mp4")
print(Downloadvideo_path+Downloadvideo_name)
uploader(Downloadvideo_path+Downloadvideo_name)