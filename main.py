import json
import requests
import urllib.parse
import time
import datetime
import random
import os
import subprocess
from cache import cache


max_api_wait_time = 8
max_time = 9.9
apis = [r"https://inv.nadeko.net/",r"https://invidious.nerdvpn.de/"]
#r"https://thingproxy.freeboard.io/fetch/https://inv.nadeko.net/",r"https://invidious.privacyredirect.com/",r"https://invidious.nerdvpn.de/",r"https://inv.odyssey346.dev/",r"https://invidious.snopyta.org/",r"https://inv.nadeko.net/",r"http://yewtu.be/",r"http://invidious.perennialte.ch/",r"https://iv.datura.network/",r"http://invidious.materialio.us/",r"https://invidious.private.coffee/",r"https://invidious.protokolla.fi/",r"https://invidious.perennialte.ch/",r"https://yt.cdaut.de/",r"https://invidious.materialio.us/",r"https://yewtu.be/",r"https://invidious.fdn.fr/",r"https://inv.tux.pizza/",r"https://invidious.privacyredirect.com/",r"https://invidious.drgns.space/",r"https://vid.puffyan.us",r"https://invidious.jing.rocks/",r"https://youtube.076.ne.jp/",r"https://vid.puffyan.us/",r"https://inv.riverside.rocks/",r"https://invidio.xamh.de/",r"https://y.com.sb/",r"https://invidious.sethforprivacy.com/",r"https://invidious.tiekoetter.com/",r"https://inv.bp.projectsegfau.lt/",r"https://inv.vern.cc/",r"https://invidious.nerdvpn.de/",r"https://inv.privacy.com.de/",r"https://invidious.rhyshl.live/",r"https://invidious.slipfox.xyz/",r"https://invidious.weblibre.org/",r"https://invidious.namazso.eu/",r"https://invidious.jing.rocks"]
url = requests.get(r'https://raw.githubusercontent.com/mochidukiyukimi/yuki-youtube-instance/main/instance.txt').text.rstrip()
version = "1.0"

os.system("chmod 777 ./yukiverify")

apichannels = []
apicomments = []
[[apichannels.append(i),apicomments.append(i)] for i in apis]
class APItimeoutError(Exception):
    pass

def is_json(json_str):
    result = False
    try:
        json.loads(json_str)
        result = True
    except json.JSONDecodeError as jde:
        pass
    return result

def apirequest(url):
    global apis
    global max_time
    starttime = time.time()
    for api in apis:
        if  time.time() - starttime >= max_time -1:
            break
        try:
            res = requests.get(api+url,timeout=max_api_wait_time)
            if res.status_code == 200 and is_json(res.text):
                return res.text
            else:
                print(f"エラー:{api}乙ー")
                apis.append(api)
                apis.remove(api)
        except:
            print(f"タイムアウト:{api}😆乙！詩寝(しね)")
            apis.append(api)
            apis.remove(api)
    raise APItimeoutError("APIがタイムアウトしました")

def apichannelrequest(url):
    global apichannels
    global max_time
    starttime = time.time()
    for api in apichannels:
        if  time.time() - starttime >= max_time -1:
            break
        try:
            res = requests.get(api+url,timeout=max_api_wait_time)
            if res.status_code == 200 and is_json(res.text):
                return res.text
            else:
                print(f"エラー:{api}")
                apichannels.append(api)
                apichannels.remove(api)
        except:
            print(f"タイムアウト:{api}")
            apichannels.append(api)
            apichannels.remove(api)
    raise APItimeoutError("APIがタイムアウトしました")

def apicommentsrequest(url):
    global apicomments
    global max_time
    starttime = time.time()
    for api in apicomments:
        if  time.time() - starttime >= max_time -1:
            break
        try:
            res = requests.get(api+url,timeout=max_api_wait_time)
            if res.status_code == 200 and is_json(res.text):
                return res.text
            else:
                print(f"エラー:{api}")
                apicomments.append(api)
                apicomments.remove(api)
        except:
            print(f"タイムアウト:{api}")
            apicomments.append(api)
            apicomments.remove(api)
    raise APItimeoutError("APIがタイムアウトしました")


def get_info(request):
    global version
    return json.dumps([version,os.environ.get('RENDER_EXTERNAL_URL'),str(request.scope["headers"]),str(request.scope['router'])[39:-2]])

def get_data(videoid):
    global logs
    t = json.loads(apirequest(r"api/v1/videos/"+ urllib.parse.quote(videoid)))
    return [{"id":i["videoId"],"title":i["title"],"authorId":i["authorId"],"author":i["author"],"error":i[error-id]} for i in t["recommendedVideos"]],list(reversed([i["url"] for i in t["formatStreams"]]))[:2],t["descriptionHtml"].replace("\n","<br>"),t["title"],t["authorId"],t["author"],t["authorThumbnails"][-1]["url"]

def get_search(q,page):
    global logs
    t = json.loads(apirequest(fr"api/v1/search?q={urllib.parse.quote(q)}&page={page}&hl=jp"))
    def load_search(i):
        if i["type"] == "video":
            return {"title":i["title"],"id":i["videoId"],"authorId":i["authorId"],"author":i["author"],"length":str(datetime.timedelta(seconds=i["lengthSeconds"])),"published":i["publishedText"],"type":"video"}
        elif i["type"] == "playlist":
            return {"title":i["title"],"id":i["playlistId"],"thumbnail":i["videos"][0]["videoId"],"count":i["videoCount"],"type":"playlist"}
        else:
            if i["authorThumbnails"][-1]["url"].startswith("https"):
                return {"author":i["author"],"id":i["authorId"],"thumbnail":i["authorThumbnails"][-1]["url"],"type":"channel"}
            else:
                return {"author":i["author"],"id":i["authorId"],"thumbnail":r"https://"+i["authorThumbnails"][-1]["url"],"type":"channel"}
    return [load_search(i) for i in t]

def get_channel(channelid):
    global apichannels
    t = json.loads(apichannelrequest(r"api/v1/channels/"+ urllib.parse.quote(channelid)))
    if t["latestVideos"] == []:
        print("APIがチャンネルを返しませんでした")
        apichannels.append(apichannels[0])
        apichannels.remove(apichannels[0])
        raise APItimeoutError("APIがチャンネルを返しませんでした")
    return [[{"title":i["title"],"id":i["videoId"],"authorId":t["authorId"],"author":t["author"],"published":i["publishedText"],"type":"video"} for i in t["latestVideos"]],{"channelname":t["author"],"channelicon":t["authorThumbnails"][-1]["url"],"channelprofile":t["descriptionHtml"]}]

def get_playlist(listid,page):
    t = json.loads(apirequest(r"/api/v1/playlists/"+ urllib.parse.quote(listid)+"?page="+urllib.parse.quote(page)))["videos"]
    return [{"title":i["title"],"id":i["videoId"],"authorId":i["authorId"],"author":i["author"],"type":"video"} for i in t]

def get_comments(videoid):
    t = json.loads(apicommentsrequest(r"api/v1/comments/"+ urllib.parse.quote(videoid)+"?hl=jp"))["comments"]
    return [{"author":i["author"],"authoricon":i["authorThumbnails"][-1]["url"],"authorid":i["authorId"],"body":i["contentHtml"].replace("\n","<br>")} for i in t]

def get_replies(videoid,key):
    t = json.loads(apicommentsrequest(fr"api/v1/comments/{videoid}?hmac_key={key}&hl=jp&format=html"))["contentHtml"]

def get_level(siawaseok):
    for i1 in range(1,13):
        with open(f'Level{i1}.txt', 'r', encoding='UTF-8', newline='\n') as f:
            if siawaseok in [i2.rstrip("\r\n") for i2 in f.readlines()]:
                return i1
    return 0


def check_cokie(cookie):
    print(cookie)
    if cookie == "True":
        return True
    return False

def get_verifycode():
    try:
        result = subprocess.run(["./yukiverify"], encoding='utf-8', stdout=subprocess.PIPE)
        hashed_password = result.stdout.strip()
        return hashed_password
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        return None





from fastapi import FastAPI, Depends
from fastapi import Response,Cookie,Request
from fastapi.responses import HTMLResponse,PlainTextResponse
from fastapi.responses import RedirectResponse as redirect
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Union


app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
app.mount("/css", StaticFiles(directory="./css"), name="static")
app.mount("/siawaseok", StaticFiles(directory="./blog", html=True), name="static")
app.mount("/pass", StaticFiles(directory="./bloger", html=True), name="static")


app.add_middleware(GZipMiddleware, minimum_size=1000)

from fastapi.templating import Jinja2Templates
template = Jinja2Templates(directory='templates').TemplateResponse






@app.get("/", response_class=HTMLResponse)
def home(response: Response,request: Request,yuki: Union[str] = Cookie(None)):
    if check_cokie(yuki):
        response.set_cookie("yuki","True",max_age=60 * 60 * 24 * 7)
        return template("home.html",{"request": request})
    print(check_cokie(yuki))
    return redirect("/siawaseok")

@app.get('/watch', response_class=HTMLResponse)
def video(v:str,response: Response,request: Request,yuki: Union[str] = Cookie(None),proxy: Union[str] = Cookie(None)):
    if not(check_cokie(yuki)):
        return redirect("/")
    response.set_cookie(key="yuki", value="True",max_age=7*24*60*60)
    videoid = v
    t = get_data(videoid)
    response.set_cookie("yuki","True",max_age=60 * 60 * 24 * 7)
    return template('video.html', {"request": request,"videoid":videoid,"videourls":t[1],"res":t[0],"description":t[2],"videotitle":t[3],"authorid":t[4],"authoricon":t[6],"author":t[5],"proxy":proxy})

@app.get("/search", response_class=HTMLResponse,)
def search(q:str,response: Response,request: Request,page:Union[int,None]=1,yuki: Union[str] = Cookie(None),proxy: Union[str] = Cookie(None)):
    if not(check_cokie(yuki)):
        return redirect("/")
    response.set_cookie("yuki","True",max_age=60 * 60 * 24 * 7)
    return template("search.html", {"request": request,"results":get_search(q,page),"word":q,"next":f"/search?q={q}&page={page + 1}","proxy":proxy})

@app.get("/hashtag/{tag}")
def search(tag:str,response: Response,request: Request,page:Union[int,None]=1,yuki: Union[str] = Cookie(None)):
    if not(check_cokie(yuki)):
        return redirect("/")
    return redirect(f"/search?q={tag}")


@app.get("/channel/{channelid}", response_class=HTMLResponse)
def channel(channelid:str,response: Response,request: Request,yuki: Union[str] = Cookie(None),proxy: Union[str] = Cookie(None)):
    if not(check_cokie(yuki)):
        return redirect("/")
    response.set_cookie("yuki","True",max_age=60 * 60 * 24 * 7)
    t = get_channel(channelid)
    return template("channel.html", {"request": request,"results":t[0],"channelname":t[1]["channelname"],"channelicon":t[1]["channelicon"],"channelprofile":t[1]["channelprofile"],"proxy":proxy})

@app.get("/answer", response_class=HTMLResponse)
def set_cokie(q:str):
    t = get_level(q)
    if t > 5:
        return f"level{t}\n推測を推奨する"
    elif t == 0:
        return "level12以上\nほぼ推測必須"
    return f"level{t}\n覚えておきたいレベル"

@app.get("/playlist", response_class=HTMLResponse)
def playlist(list:str,response: Response,request: Request,page:Union[int,None]=1,yuki: Union[str] = Cookie(None),proxy: Union[str] = Cookie(None)):
    if not(check_cokie(yuki)):
        return redirect("/")
    response.set_cookie("yuki","True",max_age=60 * 60 * 24 * 7)
    return template("search.html", {"request": request,"results":get_playlist(list,str(page)),"word":"","next":f"/playlist?list={list}","proxy":proxy})

@app.get("/info", response_class=HTMLResponse)
def viewlist(response: Response,request: Request,yuki: Union[str] = Cookie(None)):
    global apis,apichannels,apicomments
    if not(check_cokie(yuki)):
        return redirect("/")
    response.set_cookie("yuki","True",max_age=60 * 60 * 24 * 7)
    return template("info.html",{"request": request,"Youtube_API":apis[0],"Channel_API":apichannels[0],"Comments_API":apicomments[0]})

@app.get("/suggest")
def suggest(keyword:str):
    return [i[0] for i in json.loads(requests.get(r"http://www.google.com/complete/search?client=youtube&hl=ja&ds=yt&q="+urllib.parse.quote(keyword)).text[19:-1])[1]]

@app.get("/comments")
def comments(request: Request,v:str):
    return template("comments.html",{"request": request,"comments":get_comments(v)})

@app.get("/thumbnail")
def thumbnail(v:str):
    return Response(content = requests.get(fr"https://img.youtube.com/vi/{v}/0.jpg").content,media_type=r"image/jpeg")

@app.get("/bbs",response_class=HTMLResponse)
def view_bbs(request: Request,name: Union[str, None] = "",seed:Union[str,None]="",channel:Union[str,None]="main",verify:Union[str,None]="false",yuki: Union[str] = Cookie(None)):
    if not(check_cokie(yuki)):
        return redirect("/")
    res = HTMLResponse(requests.get(fr"{url}bbs?name={urllib.parse.quote(name)}&seed={urllib.parse.quote(seed)}&channel={urllib.parse.quote(channel)}&verify={urllib.parse.quote(verify)}",cookies={"yuki":"True"}).text)
    return res

@cache(seconds=5)
def bbsapi_cached(verify,channel):
    return requests.get(fr"{url}bbs/api?t={urllib.parse.quote(str(int(time.time()*1000)))}&verify={urllib.parse.quote(verify)}&channel={urllib.parse.quote(channel)}",cookies={"yuki":"True"}).text

@app.get("/bbs/api",response_class=HTMLResponse)
def view_bbs(request: Request,t: str,channel:Union[str,None]="main",verify: Union[str,None] = "false"):
    print(fr"{url}bbs/api?t={urllib.parse.quote(t)}&verify={urllib.parse.quote(verify)}&channel={urllib.parse.quote(channel)}")
    return bbsapi_cached(verify,channel)

@app.get("/bbs/result")
def write_bbs(request: Request,name: str = "",message: str = "",seed:Union[str,None] = "",channel:Union[str,None]="main",verify:Union[str,None]="false",yuki: Union[str] = Cookie(None)):
    if not(check_cokie(yuki)):
        return redirect("/")
    t = requests.get(fr"{url}bbs/result?name={urllib.parse.quote(name)}&message={urllib.parse.quote(message)}&seed={urllib.parse.quote(seed)}&channel={urllib.parse.quote(channel)}&verify={urllib.parse.quote(verify)}&info={urllib.parse.quote(get_info(request))}&serververify={get_verifycode()}",cookies={"yuki":"True"}, allow_redirects=False)
    if t.status_code != 307:
        return HTMLResponse(t.text)
    return redirect(f"/bbs?name={urllib.parse.quote(name)}&seed={urllib.parse.quote(seed)}&channel={urllib.parse.quote(channel)}&verify={urllib.parse.quote(verify)}")

@cache(seconds=30)
def how_cached():
    return requests.get(fr"{url}bbs/how").text

@app.get("/bbs/how",response_class=PlainTextResponse)
def view_commonds(request: Request,yuki: Union[str] = Cookie(None)):
    if not(check_cokie(yuki)):
        return redirect("/")
    return how_cached()

@app.get("/load_instance")
def home():
    global url
    url = requests.get(r'https://raw.githubusercontent.com/mochidukiyukimi/yuki-youtube-instance/main/instance.txt').text.rstrip()


@app.exception_handler(500)
def page(request: Request,__):
    return template("APIwait.html",{"request": request},status_code=500)

@app.exception_handler(APItimeoutError)
def APIwait(request: Request,exception: APItimeoutError):
    return template("APIwait.html",{"request": request},status_code=500)




#import logging
#import time
#from datetime import datetime, timedelta

# ロギング設定
#logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 想定処理時間を計算してログに表示する関数
#def log_with_estimated_time(start_time, estimated_duration_seconds):
    # 想定終了時刻を計算
    #estimated_end_time = start_time + timedelta(seconds=estimated_duration_seconds)
    #logging.info(f"想定終了時刻: {estimated_end_time.strftime('%Y-%m-%d %H:%M:%S')}")

# 処理開始時間
#start_time = datetime.now()

# 想定処理時間（秒）
#estimated_duration_seconds = 120  # 例えば、2分（120秒）の想定処理時間

# 処理開始ログ
#logging.info(f"処理開始時刻: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

# 想定終了時刻をログに表示
#log_with_estimated_time(start_time, estimated_duration_seconds)

# 実際の処理（ここでは単に待機時間をシミュレート）
#time.sleep(estimated_duration_seconds)

# 処理終了ログ
#end_time = datetime.now()
#logging.info(f"処理終了時刻: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")

# 処理時間を表示
#elapsed_time = end_time - start_time
#logging.info(f"実際の処理時間: {elapsed_time}")
