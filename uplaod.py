import requests
import threading
import json
import os
import hashlib
from urllib.parse import urlparse, parse_qs

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
      "parentFileId": 0,
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
 

def PutFileChunk(raw_url,byte):
    parsed_url = urlparse(raw_url)
    url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
    
    params = parse_qs(parsed_url.query)
    
    #print("Base URL:", url)
    #print("Query Parameters:", params)
    
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
    
    response =requests.put(url, params=params, data=byte, headers=headers)
    print('PutFileChunk called,status_code='+str(response.status_code))
    if 200!=response.status_code:
        return 1
    print(response.headers.get('ETag'))
    md5_hash = hashlib.md5()
    md5_hash.update(byte)
    if response.headers.get('ETag')!="\""+md5_hash.hexdigest()+"\"":
        return 2
    else:
        return 0

def CompleteUpload(upload_data,filesize):
    url = "https://www.123pan.com/b/api/file/upload_complete/v2"
    
    
    payload = json.dumps({
      "fileId": int(upload_data['FileId']),
      "bucket": upload_data['Bucket'],
      "fileSize": filesize,
      "key": upload_data['Key'],
      "isMultipart": True,
      "uploadId": upload_data['UploadId'],
      "StorageNode": upload_data['StorageNode']
    })
    
    
    
    response = requests.post(url, data=payload, headers=headers)
    while 200!=response.status_code:
        print('CompleteUpload called,status_code='+str(response.status_code))
        response = requests.post(url, data=payload, headers=headers)
    print(response.text)

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


def uploader(file_path):
    filesize = os.path.getsize(file_path)
    print(filesize)
    filename = os.path.basename(file_path)
    print(filename)
    
    md5_hash = hashlib.md5()
    with open(file_path,"rb") as f:
        # Read and update hash in chunks of 4K
        for byte_block in iter(lambda: f.read(4096),b""):
            md5_hash.update(byte_block)
        print(md5_hash.hexdigest())
    
    upload_info=json.loads(preUpload(md5_hash,filename,filesize))
        
    upload_data=upload_info['data']
    
    print('upload_info='+str(len(upload_info)))
    print('upload_data='+str(len(upload_data)))
    
    if 0==len(upload_data):
        print('err')
    else:
        if True==upload_data['Reuse']:
            print("Reuse success")
        else:
            print('\nkey:',upload_data['Key'])
            print('FileId:',upload_data['FileId'])
            print('Bucket:',upload_data['Bucket'])
            print('Reuse:',upload_data['Reuse'])
            print('UploadId:',upload_data['UploadId'])
            print('StorageNode:',upload_data['StorageNode'])
            print('SliceSize:',upload_data['SliceSize'])
            with open(file_path, 'rb') as f:
                info=CheckUploadList(upload_data,file_path)
                f.seek(info['nowsize'],0)
                start=info['nowPartNumber']
                for byte in iter(lambda: f.read(int(upload_data['SliceSize'])),b""):
        
                    upload_info=json.loads(GetUploadUrl(start,start+1,upload_data))
                    presignedUrl=upload_info['data']['presignedUrls']
                    #print('presignedUrls::'+presignedUrl[str(start)])
                    retry=0
                    while 0!=PutFileChunk(presignedUrl[str(start)],byte) and retry<6:
                        retry+=1
                        presignedUrl=json.loads(GetUploadUrl(start,start+1,upload_data))['data']['presignedUrls']
                    if retry>=6:
                        print("err")
                        return ""
                    start+=1
                    
            CompleteUpload(upload_data,filesize)
