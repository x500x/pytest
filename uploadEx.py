from concurrent.futures import ThreadPoolExecutor, as_completed,wait, ALL_COMPLETED
import time
import requests
import json
import os
import hashlib
from urllib.parse import urlparse, parse_qs
import gc

downfile_list=[]
download_flag=0 #1->have done download,0->not

headers = {
      'User-Agent': "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36",
      'Accept-Encoding': "gzip, deflate",
      'Authorization': "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MjYxMTc4NTcsImlhdCI6MTcyNTUxMzA1NywiaWQiOjE4MzczNzg4NTcsIm1haWwiOiIiLCJuaWNrbmFtZSI6IjE4OTcyOTA4NjE3Iiwic3VwcGVyIjpmYWxzZSwidXNlcm5hbWUiOjE4OTcyOTA4NjE3LCJ2IjowfQ.d4QgDvfA6ITBZ8hkBTMgj29yl2n9ktsUSiN-Bpl0v9s",
      'App-Version': "3",
      'platform': "web",
      'Content-Type': "application/json;charset=UTF-8",
      'Origin': "https://www.123pan.com",
      'X-Requested-With': "mark.via",
      'Sec-Fetch-Site': "same-origin",
      'Sec-Fetch-Mode': "cors",
      'Sec-Fetch-Dest': "empty",
      'Referer': "https://www.123pan.com/",
      'Accept-Language': "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
      }

def preUpload(md5_hash,filename,filesize):
    url = "https://www.123pan.com/b/api/file/upload_request"
    
    
    
    payload = json.dumps({
      "driveId": 0,
      "etag": md5_hash.hexdigest(),
      "fileName": str(filename),
      "parentFileId": 9411766,
      "size": filesize,
      "type": 0,
      "RequestSource": None,
      "duplicate": 2
    })
    #print(payload)
    
    
    response = requests.post(url, data=payload, headers=headers)
    while 200!=response.status_code:
        print('preUploadcalled,status_code='+str(response.status_code))
        response = requests.post(url, data=payload, headers=headers)
    #print("\n**************************\n")
    #print(response.text)
    #print('\n')
    return response.text


def GetUploadUrl(start,end,upload_data):
    url = "https://www.123pan.com/b/api/file/s3_repare_upload_parts_batch"
    
    
    payload = json.dumps({
      "bucket": upload_data['Bucket'],
      "key": upload_data['Key'],
      "partNumberEnd": end,
      "partNumberStart": start,
      "uploadId": upload_data['UploadId'],
      "StorageNode": upload_data['StorageNode']
    })
    
    
    
    response = requests.post(url, data=payload, headers=headers)
    while 200!=response.status_code:
        print('GetUploadUrlcalled,status_code='+str(response.status_code))
        response = requests.post(url, data=payload, headers=headers)
    #print("\n**************************\n")
    #print(response.text)
    #print('\n')
    return response.text
    
def CompleteUpload(upload_data):
    url = "https://www.123pan.com/b/api/file/upload_complete/v2"
    
    
    payload = json.dumps({
      "fileId": int(upload_data['FileId']),
      "bucket": upload_data['Bucket'],
      "fileSize": upload_data['filesize'],
      "key": upload_data['Key'],
      "isMultipart": True,
      "uploadId": upload_data['UploadId'],
      "StorageNode": upload_data['StorageNode']
    })
    
    
    
    response = requests.post(url, data=payload, headers=headers)
    retry=0
    while 200!=response.status_code and retry<5:
        print('CompleteUpload called,status_code='+str(response.status_code))
        response = requests.post(url, data=payload, headers=headers)
        retry+=1
    print(response.text)

def PutFileChunk(part,upload_data,byte):
    #global uploadInfo_lists
    #print(f'PutFileChunk called,part={part},upload_data={upload_data}')
    headers = {
      'User-Agent': "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36",
      'Accept-Encoding': "gzip, deflate",
      'Content-Type': "application/octet-stream",
      'Origin': "https://www.123pan.com",
      'X-Requested-With': "mark.via",
      'Sec-Fetch-Site': "cross-site",
      'Sec-Fetch-Mode': "cors",
      'Sec-Fetch-Dest': "empty",
      'Referer': "https://www.123pan.com/",
      'Accept-Language': "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7"
    }
    retry=0
    while retry<6:
        raw_url=json.loads(GetUploadUrl(part,part+1,upload_data))['data']['presignedUrls'][str(part)]
        #print(raw_url)
        parsed_url = urlparse(raw_url)
        url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
        
        params = parse_qs(parsed_url.query)
        
        
        #print("Base URL:", url)
        #print("Query Parameters:", params)
        
        response =requests.put(url, params=params, data=byte, headers=headers)
        print('PutFileChunk called,status_code='+str(response.status_code))
        if 200!=response.status_code:
            retry+=1
            continue
        else:
            retry=0
        print(response.headers.get('ETag'))
        md5_hash = hashlib.md5()
        md5_hash.update(byte)
        if response.headers.get('ETag')!="\""+md5_hash.hexdigest()+"\"":
            retry+=1
            print("PutFileChunk err")
            continue
        else:
            del byte
            gc.collect()
            return int(upload_data['FileId'])
    del byte
    gc.collect()
    return -1        
    
def CheckUploadList(upload_data,filepath):
    url = "https://www.123pan.com/b/api/file/s3_list_upload_parts"
    
    payload = json.dumps({
      "bucket": upload_data['Bucket'],
      "key": upload_data['Key'],
      "uploadId": upload_data['UploadId'],
      "StorageNode": upload_data['StorageNode']
    })
    
    
    response = requests.post(url,  data=payload, headers=headers)
    while 200!=response.status_code:
        print('CheckUploadListcalled,status_code='+str(response.status_code))
        response = requests.post(url,  data=payload, headers=headers)
    print(response.text)
    json_obj=json.loads(response.text)['data']['Parts']
    info={
        "nowsize":0,
        "nowPartNumber":0
    }
    if isinstance(json_obj,type(None)):
        print('isNoneType\n')
        info['nowPartNumber']+=1
        return info
    with open(filepath,"rb") as f:
        for obj in json_obj:
            ETag = obj.get('ETag')
            byte=f.read(int(obj.get('Size')))
            md5_hash = hashlib.md5()
            md5_hash.update(byte)
            if ETag!="\""+md5_hash.hexdigest()+"\"":
                presignedUrl=json.loads(GetUploadUrl(int(obj.get('PartNumber')),int(obj.get('PartNumber'))+1,upload_data))['data']['presignedUrls']
                retry=0
                while 0!=PutFileChunk(presignedUrl[str(int(obj.get('PartNumber')))],byte) and retry<6:
                    presignedUrl=json.loads(GetUploadUrl(int(obj.get('PartNumber')),int(obj.get('PartNumber'))+1,upload_data))['data']['presignedUrls']
                if retry>=6:
                    break
            info['nowPartNumber'] = int(obj.get('PartNumber'))
            info['nowsize'] += int(obj.get('Size'))
            print(f"PartNumber: {obj.get('PartNumber')}, Size: {obj.get('Size')},ETag: {ETag}")
            print('nowsize='+str(info['nowsize']))
    info['nowPartNumber']+=1
    return info
    
def CheckThreadStatus(task_lists,upload_data_list):
    #print("CheckThreadStatus called")
    #time.sleep(12)
    #return
    for task in task_lists:
        if task.done():
            #print("CheckThreadStatus one done")
            #print(task)
            #print(str(task.result()))
            try:
                if task.result()>=0:
                    #print(str(task.result()))
                    upload_data=upload_data_list[task.result()]
                    #print(upload_data)
                    upload_data['nowpartnumber']+=1
                    if upload_data['nowpartnumber']==upload_data['parts']:
                        
                        
                        CompleteUpload(upload_data)
                else:
                    print('there hava an error about putfile')
            except Exception as e:
                print(f"Task failed: {e}")
            task_lists.remove(task)

def uploader():
    global download_flag
    start=1
    #fileinfo=""
    task_lists=[] #线程池所有已提交任务列表
    upload_data_list={}
    max_workers=5
    
    
    
    # = ThreadPoolExecutor(max_workers=max_workers)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        while True:
            start=1
            file_path=""
            filename=""
            filesize=0
            #print('loop')
            #fileinfo[filepath]=f.readline().strip().replace('\n',''))
            if len(downfile_list)==0 and download_flag==1:
                #print('case 1')
                wait(task_lists,return_when=ALL_COMPLETED)
                CheckThreadStatus(task_lists,upload_data_list)
                #print(f"beforeDel lentask={len(task_lists)}")
                del task_lists
                print('all upload finished.')
                break
            if len(downfile_list)==0 and download_flag==0:
                #print(f'{download_flag}case 2')
                time.sleep(1)
                continue
            else:
                #with lock:
                file_path=downfile_list.pop()
                print("path"+file_path)
                if ""==file_path:
                    break
                #    del downfile_list[0]
            
            filesize = os.path.getsize(file_path)
            #print(fileinfo[filesize])
            filename = os.path.basename(file_path)
            print(filename)
            
            
            md5_hash = hashlib.md5()
            with open(file_path,"rb") as f:
                # Read and update hash in chunks of 4K
                for byte_block in iter(lambda: f.read(4096),b""):
                    md5_hash.update(byte_block)
                print(md5_hash.hexdigest())
            
            
            #task_lists.append(executor.submit())
            
            upload_data=json.loads(preUpload(md5_hash,filename,filesize))['data']
            
            #print('upload_info='+str(len(upload_info)))
            #print('upload_data='+str(len(upload_data)))
            
            if 0==len(upload_data):
                print('get upload_data err')
            else:
                if True==upload_data['Reuse']:
                    print("Reuse success")
                else:
                    if filesize%int(upload_data['SliceSize'])==0:
                        upload_data['parts']=filesize//int(upload_data['SliceSize'])
                    else:
                        upload_data['parts']=(filesize//int(upload_data['SliceSize']))+1
                    print('\nReuse:',upload_data['Reuse'])
                    
                    print(f"parts={upload_data['parts']}")
                    upload_data['nowpartnumber']=0
                    upload_data['filesize']=filesize
                    upload_data_list[int(upload_data['FileId'])]=upload_data
                    print(upload_data_list[int(upload_data['FileId'])])
                    
                    with open(file_path, 'rb') as f:
                        info=CheckUploadList(upload_data,file_path)
                        f.seek(info['nowsize'],0)
                        start=info['nowPartNumber']
                        #fileinfo[fileparts]=fileinfo[fileparts]-(info['nowPartNumber']-1)
                        
                        
                        for byte in iter(lambda: f.read(int(upload_data['SliceSize'])),b""):
                            while True:
                                if len(task_lists)<8:
                                    task_lists.append(executor.submit(lambda cxp:PutFileChunk(*cxp),(start,upload_data,byte)))
                                    #task_lists.append(executor.submit(PutFileChunk,start,upload_data,byte))
                                    print(f"a task has append,now tasklen={len(task_lists)}")
                                    start+=1
                                    break
                                #else:
                                #    pass
                                    #prepareForFutureUpload()
                                CheckThreadStatus(task_lists,upload_data_list)
                                time.sleep(1)
                    CheckThreadStatus(task_lists,upload_data_list)
                    #if len(task_lists)==0:
                    #    break
        #wait(task_lists,return_when=ALL_COMPLETED)            
                
                        
    #executor.shutdown(wait=True)
                        
                

