import os
#import 123uplaod
from uplaod import uploader
#\'\\r\\n\'

#--format=flv1080
Downloadvideo_path="D:\\a\\pytest\\pytest\\"
Downloadvideo_name="1.mp4"
#os.system("you-get https://b23.tv/CstBqCK -i -c .\\c.txt")
os.system("you-get https://b23.tv/CstBqCK -O 1 -o D:\\a\\pytest\\pytest\\ -c .\\c.txt")
print(Downloadvideo_path+Downloadvideo_name)
uploader(Downloadvideo_path+Downloadvideo_name)