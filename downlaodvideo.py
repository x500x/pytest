# -*- coding: UTF-8 -*-
#from icecream import ic
import requests
import re
import json
import os
from concurrent.futures import ProcessPoolExecutor
import threading
from uploadEx import uploader
import sys
import io
import subprocess

def downloader(url, local_filename):
    headers = {
  'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
  'referer': "https://www.bilibili.com"
    }
    with requests.get(url, headers=headers,stream=True) as r:
        try:
        
            #r.raise_for_status()
            with open(local_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024*1024):
                    if chunk:
                        f.write(chunk)
                        f.flush()
        except Exception as e:
           print("err:", str(e))
           r.raise_for_status()
           return 1
    return 0




def ProcessTask(video_url,audio_url,file_path):
    if 0!=downloader(video_url,file_path+'[00].m4s'):
        if 0!=downloader(video_url,file_path+'[00].m4s'):
            #print("downerr::"+file_path.encode()+'[00].m4s')
            return ""
    if 0!=downloader(audio_url,file_path+'[01].m4s'):
        if 0!=downloader(audio_url,file_path+'[01].m4s'):
            #print("downerr::"+file_path+'[01].m4s')
            return ""
    ret=subprocess.call(f".\\ffmpeg-7.0.2-full_build\\bin\\ffmpeg.exe -i {file_path}[00].m4s -i {file_path}[01].m4s -c:v copy -c:a copy -f mp4 {file_path}.mp4", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,shell=True)
    #ret=subprocess.call(f".\\ffmpeg-7.0.2-full_build\\bin\\ffmpeg.exe -i {file_path}[00].m4s -i {file_path}[01].m4s -c:v copy -c:a copy -f mp4 {file_path}.mp4",shell=True)
    print(f"ret={ret}")
    #if os.path.isfile(file_path+'[00].m4s'): print("exist 00")
    #if os.path.isfile(file_path+'[01].m4s'): print("exist 01")

    try:
        os.remove(file_path+'[00].m4s')
        os.remove(file_path+'[01].m4s')
        #print(f'File {file_path} deleted successfully.')
    except OSError as e:
        print(f'Error occurred: {e}')
    if os.path.isfile(file_path+".mp4"):
        print("file downed")
        return file_path+".mp4"
    else:
        print("file does not exist")
        return ""
    


 
def assignTask(f):
    #global downfile_list #for 123
    #global downfilelist #for github
    #global download_flag
    process_lists=[]
    try:
        with ThreadPoolExecutor(max_workers=3) as executor:
            while True:
                video_url=f.readline().strip()
                audio_url=f.readline().strip()
                name=f.readline().strip()
                if video_url=="" or audio_url=="" or name=="":
                    break
                p=executor.submit(ProcessTask,video_url,audio_url,"C:\\"+name)
                process_lists.append(p)
    except Exception as err:
        print(f"when assignTask had an err:\n{err}")
    except BaseException as err:
        print(f"when assignTask had an err:\n{err}")
    uploader(process_lists)

        
 
if __name__ == '__main__':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    with open(os.getcwd()+'\\info.txt',"r", encoding='utf-8') as f:
        assignTask(f)
    
    
    #print(downfile_list)
    print("done")