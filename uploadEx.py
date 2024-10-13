from concurrent.futures import ThreadPoolExecutor, as_completed,wait, ALL_COMPLETED
import time
import random
import requests
import json
import os
import hashlib
from urllib.parse import urlparse, parse_qs
import gc

downfile_list=[]
download_flag=0 #1->have done download,0->not

def ChangeVar(downfilepath='',downloadflag=0):
    global downfile_list
    global download_flag
    #print(downfilepath)
    #print(str(downloadflag))
    if downfilepath!="": downfile_list.append(downfilepath)
    download_flag=downloadflag
    #print(f"ChangeVar Called,downfile_list={downfile_list},download_flag={download_flag}")

headers = {
      'User-Agent': "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36",
      'Accept-Encoding': "gzip, deflate",
      'Authorization': "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3Mjg4ODA5OTAsImlhdCI6MTcyODI3NjE5MCwiaWQiOjE4MzczNzg4NTcsIm1haWwiOiIiLCJuaWNrbmFtZSI6IjE4OTcyOTA4NjE3Iiwic3VwcGVyIjpmYWxzZSwidXNlcm5hbWUiOjE4OTcyOTA4NjE3LCJ2IjowfQ.Uox9jz-980XWcg8GWBGJdsHPQrY79kEEqWmoEyIVGuE",
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
      "parentFileId": 9582564,
      "size": filesize,
      "type": 0,
      "RequestSource": None,
      "duplicate": 2
    })
    #print(payload)
    
    
    response = requests.post(url, data=payload, headers=headers)
    while 200!=response.status_code:
        #print('preUploadcalled,status_code='+str(response.status_code))
        response = requests.post(url, data=payload, headers=headers)
    #print("\n**************************\n")
    #print(response.text)
    #print('\n')
    return response.text


def GetUploadUrl(start,end,upload_data):
    re_try=0
    url = "https://www.123pan.com/b/api/file/s3_repare_upload_parts_batch"
    
    
    payload = json.dumps({
      "bucket": upload_data['Bucket'],
      "key": upload_data['Key'],
      "partNumberEnd": end,
      "partNumberStart": start,
      "uploadId": upload_data['UploadId'],
      "StorageNode": upload_data['StorageNode']
    })
    
    while re_try<5:
        try:
            response = requests.post(url, data=payload, headers=headers)
            while 200!=response.status_code:
                #print('GetUploadUrlcalled,status_code='+str(response.status_code))
                response = requests.post(url, data=payload, headers=headers)
            #print("\n**************************\n")
            #print(response.text)
            #print('\n')
            return response.text
        except Exception as err:
            re_try+=1
            time.sleep(random.random())
            print(f"when CheckUploadList had an err:\n{err}")
        except BaseException as err:
            re_try+=1
            time.sleep(random.random())
            print(f"when CheckUploadList had an err:\n{err}")
    
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
        #print(response.headers.get('ETag'))
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
    re_try=0
    url = "https://www.123pan.com/b/api/file/s3_list_upload_parts"
    
    payload = json.dumps({
      "bucket": upload_data['Bucket'],
      "key": upload_data['Key'],
      "uploadId": upload_data['UploadId'],
      "StorageNode": upload_data['StorageNode']
    })
    while re_try<5:
        try:
            response = requests.post(url,  data=payload, headers=headers)
            while 200!=response.status_code:
                print('CheckUploadListcalled,status_code='+str(response.status_code))
                response = requests.post(url,  data=payload, headers=headers)
            #print(response.text)
            json_obj=json.loads(response.text)['data']['Parts']
            info={
                "nowsize":0,
                "nowPartNumber":0
            }
            if isinstance(json_obj,type(None)):
                #print('isNoneType\n')
                info['nowPartNumber']+=1
                return info
            with open(filepath,"rb") as f:
                for obj in json_obj:
                    ETag = obj.get('ETag')
                    byte=f.read(int(obj.get('Size')))
                    md5_hash = hashlib.md5()
                    md5_hash.update(byte)
                    if ETag!="\""+md5_hash.hexdigest()+"\"":
                        PutFileChunk(int(obj.get('PartNumber')),upload_data,byte)
                    info['nowPartNumber'] = int(obj.get('PartNumber'))
                    upload_data["nowpartcount"]+=1
                    info['nowsize'] += int(obj.get('Size'))
                    #print(f"PartNumber: {obj.get('PartNumber')}, Size: {obj.get('Size')},ETag: {ETag}")
                    #print('nowsize='+str(info['nowsize']))
            info['nowPartNumber']+=1
            return info
        except Exception as err:
            re_try+=1
            time.sleep(random.random())
            print(f"when CheckUploadList had an err:\n{err}")
        except BaseException as err:
            re_try+=1
            time.sleep(random.random())
            print(f"when CheckUploadList had an err:\n{err}")
    
def CheckThreadStatus(task_lists,upload_data_list):
    
    #time.sleep(12)
    #return
    for i in range(0,len(task_lists)):
        #task=task_lists[i]
        task=task_lists.pop(0)
        #print("CheckThreadStatus called")
        if task.done():
            print(f"CheckThreadStatus one done,lentask={len(task_lists)}")
            #print()
            #print(str(task.result()))
            try:
                if task.result()>=0:
                    #print(str(task.result()))
                    upload_data=upload_data_list[task.result()]
                    #print(upload_data)
                    upload_data['nowpartcount']+=1
                    #print(f"CheckThreadStatus called,nowpartnumber={upload_data['nowpartnumber']},parts={upload_data['parts']}")
                    if upload_data['nowpartcount']==upload_data['parts']:
                        
                        CompleteUpload(upload_data)
                        del upload_data_list[task.result()]
                        
                        #print(f"del one upload_data_list done,NowLenupload_data_list={len(upload_data_list)}")
                        try:
                            os.remove(upload_data['filepath'])
                        except OSError as e:
                            print(f'Error occurred: {e}')
                else:
                    print('there hava an error about putfile')
            except Exception as e:
                print(f"Task failed: {e}")
            #del task_lists[i]
            
            #print(f"del one task_lists done,NowLenTask={len(task_lists)}")
        else:
            task_lists.append(task)

def uploader(process_lists):
    #print("start upload")
    try:
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
                    try:
                        for i in range(0,len(process_lists)):
                            task=process_lists.pop(0)
                            if task.done():
                                #print("")
                                print("task done,result:"+task.result())
                                if task.result()!="":
                                    ChangeVar(downfilepath=task.result())
                            else:
                                process_lists.append(task)
                    except Exception as err:
                        print(f"in uploader when assignTask had an err:\n{err}")
                        ChangeVar(downloadflag=1)
                    except BaseException as err:
                        print(f"in uploader when assignTask had an err:\n{err}")
                        ChangeVar(downloadflag=1)
                    if len(process_lists)==0:
                        ChangeVar(downloadflag=1)
                    CheckThreadStatus(task_lists,upload_data_list)
                    time.sleep(1)
                    continue
                #elif len(downfile_list)>0:
                else:
                    #with lock:
                    file_path=downfile_list.pop(0)
                    #print("path:"+file_path)
                    if ""==file_path:
                        break
                    #    del downfile_list[0]
                
                filesize = os.path.getsize(file_path)
                #print(fileinfo[filesize])
                filename = os.path.basename(file_path)
                #print(filename)
                
                
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
                
                if isinstance(upload_data,type(None)):
                    print('get upload_data err')
                else:
                    if True==upload_data['Reuse']:
                        print("Reuse success")
                    else:
                        if filesize%int(upload_data['SliceSize'])==0:
                            upload_data['parts']=filesize//int(upload_data['SliceSize'])
                        else:
                            upload_data['parts']=(filesize//int(upload_data['SliceSize']))+1
                        #print('\nReuse:',upload_data['Reuse'])
                        
                        #print(f"parts={upload_data['parts']}")
                        #upload_data['nowpartnumber']=0
                        upload_data["nowpartcount"]=0
                        upload_data['filesize']=filesize
                        upload_data['filepath']=file_path
                        upload_data_list[int(upload_data['FileId'])]=upload_data
                        #print(upload_data_list[int(upload_data['FileId'])])
                        
                        info=CheckUploadList(upload_data,file_path)
                        start=info['nowPartNumber']
                        
                        print(upload_data_list[int(upload_data['FileId'])])
                        if upload_data["nowpartcount"]==upload_data['parts']:
                            CompleteUpload(upload_data)
                            try:
                                os.remove(upload_data['filepath'])
                            except OSError as e:
                                print(f'Error occurred: {e}')
                            continue
                        with open(file_path, 'rb') as f:
                            
                            f.seek(info['nowsize'],0)
                            
                            for byte in iter(lambda: f.read(int(upload_data['SliceSize'])),b""):
                                while True:
                                    if len(task_lists)<max_workers+3:
                                        task_lists.append(executor.submit(lambda cxp:PutFileChunk(*cxp),(start,upload_data,byte)))
                                        #task_lists.append(executor.submit(PutFileChunk,start,upload_data,byte))
                                        print(f"a task has append({filename}),now tasklen={len(task_lists)}")
                                        start+=1
                                        break
                                    else:
                                        CheckThreadStatus(task_lists,upload_data_list)
                                        time.sleep(1)
                        
                        #CheckThreadStatus(task_lists,upload_data_list)
    except KeyboardInterrupt:
        pass
    except Exception as err:
        print(f"in upload had an err:\n{err}")
    except BaseException as err:
        print(f"in upload had an err:\n{err}")
                    #if len(task_lists)==0:
                    #    break
        #wait(task_lists,return_when=ALL_COMPLETED)            
                
                        
    #executor.shutdown(wait=True)
                        
                

