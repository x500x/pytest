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
            return ''
    if 0!=downloader(audio_url,file_path+'[01].m4s'):
        if 0!=downloader(audio_url,file_path+'[01].m4s'):
            print("downerr::"+file_path+'[01].m4s')
            return ''
    os.system(f".\\ffmpeg-7.0.2-full_build\\bin\\ffmpeg.exe -i {file_path}[00].m4s -i {file_path}[01].mp4 -c:v copy -c:a copy -f mp4 {file_path}.mp4")
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
    
def GetVideoUrl(bvid,cid):
    url = "https://api.bilibili.com/x/player/wbi/playurl"
    
    params = {
      #'avid': "113079677358064",
      'bvid': str(bvid),
      'cid': str(cid),
      'qn': "80",
      'fnver': "0",
      'fnval': "4048",
      'fourk': "1",
      'gaia_source': "",
      'from_client': "BROWSER",
      'is_main_page': "true",
      'need_fragment': "false",
      'isGaiaAvoided': "false",
      'session': "422820c13f2ecbd75d6abea9c15057b0",
      'voice_balance': "1",
      'web_location': "1315873"
    }
    
    headers = {
      'User-Agent': "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36",
      'Accept': "application/json, text/plain, */*",
      'Accept-Encoding': "gzip, deflate",
      'origin': "https://www.bilibili.com",
      'x-requested-with': "mark.via",
      'sec-fetch-site': "same-site",
      'sec-fetch-mode': "cors",
      'sec-fetch-dest': "empty",
      'referer': "https://www.bilibili.com",
      'accept-language': "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
      'Cookie': "buvid3=262D7070-E130-9F55-9D42-98C995D524F590651infoc; b_nut=1708175490; _uuid=D1028DD5A-29EB-377C-4A99-E102539563AA392917infoc; buvid4=BD8FEA68-08A8-B28D-6BC6-70023A6643CE93035-124021713-pYdguYw9VMhQEP7Z3DDf+g%3D%3D; buvid_fp=cae4ff07cbccaf2d9ad7c382f475ca1e; header_theme_version=CLOSE; enable_web_push=DISABLE; home_feed_column=4; browser_resolution=1100-2038; CURRENT_FNVAL=4048; rpdid=|(um~kmmmuRR0J'u~kJ|k~|uu; bsource_origin=share_source_copy_link; bsource=share_source_copy_link; b_lsid=84A56233_191F3F7CD7B; bili_ticket=eyJhbGciOiJIUzI1NiIsImtpZCI6InMwMyIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MjY2MzQxOTgsImlhdCI6MTcyNjM3NDkzOCwicGx0IjotMX0.OyhYUKZD_yZtZ7paJMVXwXV3TlVQaWES_edYj0Nx-Yw; bili_ticket_expires=1726634138; SESSDATA=04f58f3c%2C1741927067%2C744f3%2A92CjAUDVdn7SIkv0YDw2M4LsIrO6i_e2HMc6TgWohZgXZ44w94_91cr89zgfx8FUpV7WQSVlA2Q3RQeHBja0hRbkdiai1SaWtzT3VuTy03T2hFOEhsaGxvNXNPR2dXMHB1ZERDSGFBSGdhVk5GYXUxa2w4cVQ2emZuZnBHeTlEUFpwSUtIbDBhODZnIIEC; bili_jct=41714ce64b2c0dbd29994cee8b050ce9; DedeUserID=675239530; DedeUserID__ckMd5=f64e0c0b1ff30cc0; sid=6ydzy6fo; CURRENT_QUALITY=80"
    }
    
    response = requests.get(url, params=params, headers=headers)
    #print('')
    print("cid::"+str(cid))
    print(response.text)
    #data = json.loads(json_data)

    # 获取 baseUrl
    #base_url = response.text.data['data']['dash']['video'][0]['baseUrl']


    #print(json.loads(response.text)['data']['dash']['video'][0]['baseUrl'].strip())
    #print(json.loads(response.text)['data']['dash']['video'][0]['base_url'].strip())
    return json.loads(response.text)['data']['dash']['video'][0]['baseUrl'].strip(),json.loads(response.text)['data']['dash']['video'][0]['base_url'].strip()
    #print('***********************')
    #print('')

def fin_data(_url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
    }
     
    try:
        get_url = requests.get(url=_url, headers=headers)
        get_url.raise_for_status()
        #print(get_url.text)
        return get_url.text
     
    except requests.RequestException as e:
        print(f"请求失败: {e}")
        return None
 
def extract_and_process_content(content):
    global downfile_list #for 123
    #global downfilelist #for github
    global download_flag
    # 使用正则表达式提取部分内容
    #pattern = re.compile(r'"part":"([^"]+)"')
    #pattern = 
    #matches = pattern
    #print(content)
    process_lists=[]
    bvid = re.search(r'"bvid":"([^"]+)"',content)
    if bvid:
        print(bvid.group(1))
    else:
        print("do not match")
    cid_lists=re.compile(r'"cid":(\d+)').findall(content)
    part_lists=re.compile(r'"part":"([^"]+)"').findall(content)
    
    print(str(len(part_lists)))
    #def decode_unicode(text):
    #    return json.loads('"' + text + '"')
 
    # 打印提取的并转换后的内容
    start=0
    with ProcessPoolExecutor(max_workers=3) as executor:
        for i in range(start,start+1):
            if i>len(part_lists)-1:
                print('auto finish')
                break
            #decoded_content = decode_unicode(part_lists[i])
            #GetVideoUrl(cid_lists[i+1])
            #print(part_lists[i].strip()+".mp4")
            #print('cid:'+str(cid_lists[i+1]))
            video_url,audio_url=GetVideoUrl(bvid.group(1),cid_lists[i+1])
            
            p=pool.submit(ProcessTask, args=(video_url,audio_url,".\\"+part_lists[i].strip()))
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
    url = 'https://b23.tv/CstBqCK'  # 替换为实际的网页链接
    #filepath='/data/user/0/coding.yu.pythoncompiler.new/files/1.txt'
    webpage_content = fin_data(url)
    #i=0
    t=threading.Thread(target=uploader)
    if webpage_content:
        #with open(filepath,"w", encoding='utf-8') as f:
        #    #print(str(i))
        #    extract_and_process_content(webpage_content,f)
        t.start()
        extract_and_process_content(webpage_content)
    #ftp_upload(filepath)
    #t.join()
    print("done")
    