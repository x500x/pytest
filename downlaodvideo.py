import os
#import 123uplaod
from uplaod import uploader
#\'\\r\\n\'
header_arg='-user_agent "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36" -headers "referer: \'https://www.bilibili.com\'"$"origin: \'https://www.bilibili.com\''
print(header_arg)
video_url="https://upos-sz-mirrorcos.bilivideo.com/upgcxcode/53/73/1167117353/1167117353-1-30080.m4s?e=ig8euxZM2rNcNbdlhoNvNC8BqJIzNbfqXBvEqxTEto8BTrNvN0GvT90W5JZMkX_YN0MvXg8gNEV4NC8xNEV4N03eN0B5tZlqNxTEto8BTrNvNeZVuJ10Kj_g2UB02J0mN0B5tZlqNCNEto8BTrNvNC7MTX502C8f2jmMQJ6mqF2fka1mqx6gqj0eN0B599M=&uipk=5&nbs=1&deadline=1726934079&gen=playurlv2&os=cosbv&oi=0&trid=ba3df8b123be45388d99d97a97bb88f9u&mid=675239530&platform=pc&og=cos&upsig=24683a6fb34c598f8901046f69bfcc7d&uparams=e,uipk,nbs,deadline,gen,os,oi,trid,mid,platform,og&bvc=vod&nettype=0&orderid=0,3&buvid=262D7070-E130-9F55-9D42-98C995D524F590651infoc&build=0&f=u_0_0&agrr=0&bw=45583&logo=80000000"
audio_url="https://upos-sz-mirrorcos.bilivideo.com/upgcxcode/53/73/1167117353/1167117353-1-30080.m4s?e=ig8euxZM2rNcNbdlhoNvNC8BqJIzNbfqXBvEqxTEto8BTrNvN0GvT90W5JZMkX_YN0MvXg8gNEV4NC8xNEV4N03eN0B5tZlqNxTEto8BTrNvNeZVuJ10Kj_g2UB02J0mN0B5tZlqNCNEto8BTrNvNC7MTX502C8f2jmMQJ6mqF2fka1mqx6gqj0eN0B599M=&uipk=5&nbs=1&deadline=1726934079&gen=playurlv2&os=cosbv&oi=0&trid=ba3df8b123be45388d99d97a97bb88f9u&mid=675239530&platform=pc&og=cos&upsig=24683a6fb34c598f8901046f69bfcc7d&uparams=e,uipk,nbs,deadline,gen,os,oi,trid,mid,platform,og&bvc=vod&nettype=0&orderid=0,3&buvid=262D7070-E130-9F55-9D42-98C995D524F590651infoc&build=0&f=u_0_0&agrr=0&bw=45583&logo=80000000"

Downloadvideo_path=".\\1.mp4"

os.system("ffmpeg "+header_arg+" -i "+video_url+" -i "+audio_url+" -c:v copy -c:a copy -f mp4 "+Downloadvideo_path)
uploader(Downloadvideo_path)