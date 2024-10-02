# -*- coding: UTF-8 -*-
#from icecream import ic
import requests
import re
import json
import os
from concurrent.futures import ProcessPoolExecutor
import threading
from uploadEx import uploader,download_flag,downfile_list
import sys
import io
import subprocess
from urllib.parse import urlparse, parse_qs
import urllib.error
import urllib.request

def downloader(url, local_filename):
    opener = urllib.request.build_opener()
    # 构建请求头列表每次随机选择一个
    opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0')]
    urllib.request.install_opener(opener)
    try:
       urllib.request.urlretrieve(url, local_filename)
       print("file download success")
       return 0
    except urllib.error.HTTPError as e:
       print("HTTPError:", str(e))
       return 1
    except urllib.error.URLError as e:
       print("URLError:", str(e))
       return 2
    except Exception as e:
       print("err:", str(e))
       return 3


def ProcessTask(video_url,audio_url,file_path):
    if 0!=downloader(video_url,file_path+'[00].m4s'):
        if 0!=downloader(video_url,file_path+'[00].m4s'):
            print("downerr::"+file_path+'[00].m4s')
            return ""
    if 0!=downloader(audio_url,file_path+'[01].m4s'):
        if 0!=downloader(audio_url,file_path+'[01].m4s'):
            print("downerr::"+file_path+'[01].m4s')
            return ""
    subprocess.call(f".\\ffmpeg-7.0.2-full_build\\bin\\ffmpeg.exe -i {file_path}[00].m4s -i {file_path}[01].mp4 -c:v copy -c:a copy -f mp4 {file_path}.mp4", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        os.remove(file_path+'[00].m4s')
        os.remove(file_path+'[01].m4s')
        #print(f'File {file_path} deleted successfully.')
    except OSError as e:
        print(f'Error occurred: {e}')
    if os.path.isfile(file_path+".mp4"):
        return file_path+".mp4"
    else:
        return ""
    


 
def assignTask(f):
    global downfile_list #for 123
    #global downfilelist #for github
    global download_flag
    process_lists=[]
    with ProcessPoolExecutor(max_workers=3) as executor:
        while True:
            video_url=f.readline().strip()
            audio_url=f.readline().strip()
            name=f.readline().strip()
            if video_url=="" or audio_url=="" or name=="":
                #download_flag=1
                #print("when read file,there has a err")
                break
            p=executor.submit(ProcessTask,video_url,audio_url,name)
            process_lists.append(p)
            #wait()
            for task in process_lists:
                if task.done():
                    if task.result()!="":
                        downfile_list.append(task.result())
                        #downfilelist.append(task.result())
                    process_lists.remove(task)
        while len(process_lists)!=0:
            for task in process_lists:
                if task.done():
                    if task.result()!="":
                        downfile_list.append(task.result())
                        #downfilelist.append(task.result())
                    process_lists.remove(task)
    download_flag=1

        
 
if __name__ == '__main__':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    with open(os.getcwd()+'\\info.txt',"r", encoding='utf-8') as f:
      t=threading.Thread(target=assignTask,args=(f,))
      t.start()
      uploader()
      t.join()
    
    t.join()
    print("done")
    