import os
#import 123uplaod
from uplaod import uploader
#\'\\r\\n\'

Downloadvideo_path="C:\\videos"
Downloadvideo_name="1.mp4"
#os.system("you-get https://b23.tv/CstBqCK -i -c .\\c.txt")
os.system("you-get https://b23.tv/CstBqCK -O 1 -o C:\\videos -c .\\c.txt")
os.system("dir C:\\videos /s")
print(Downloadvideo_path+Downloadvideo_name)
uploader(Downloadvideo_path+Downloadvideo_name)