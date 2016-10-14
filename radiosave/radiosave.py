import threading
import os
import requests
import datetime
import time
import json

"""
#PROJECT PLAN
Level 1: Save webradio stream for given duration -done
Level 2: Save webradio stream for given time frame in the future -done
Level 3: Add and remove radio stream urls
Level 4: WEB-APP! with Flask
"""

def rec(streamurl, outputdir, duration):
    stop = threading.Event()
    record_thread = threading.Thread(target=rec_worker, args=(stop, streamurl, outputdir))
    record_thread.setDaemon(True)
    record_thread.start()
    record_thread.join(duration)
    
    if record_thread.is_alive:
        stop.set()

def time_call(starttime):
    #helper thread for scheduling the record start
    while datetime.datetime.now() < starttime:
        time.sleep(.5)
    
        

def timer(starttime, endtime, url, outputdir):
    starttime -= datetime.timedelta(minutes=1)
    endtime += datetime.timedelta(minutes=1)
    stop = threading.Event()
    timer_thread = threading.Thread(target = time_call, args=([starttime]))
    timer_thread.setDaemon(True)
    
    timer_thread.start()
    timer_thread.join()
    
    if timer_thread.is_alive():
        stop.set()
    
    if datetime.datetime.now() < endtime:
        seconds = (endtime - datetime.datetime.now()).seconds
    
        print seconds/60.0
        print "Now starting record!"
        rec(url, outputdir, seconds)
        print "Record finished!"

    else:
        print "Record time is in the past. Nothing to do."

def future_rec(streamurl, outputdir, starttime, endtime):
    now_string = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    sometime = datetime.datetime.strptime("2016-10-13 11:55", "%Y-%m-%d %H:%M")
    print sometime-datetime.datetime.now()
    #print datetime.datetime.isoformat(datetime.datetime.now())

def parse_mpegurl(mpegurl_content):
    res = []
    for line in mpegurl_content:
        line = line.strip()
        if "#" not in line and line != "":
            res.append(line)
    return res

"""    
#test maybe necessary for multiple stream url entries. 
#If one is not working, try until success, else report failure
def test_streamurl(url):
    r = requests.get(url, stream = True)
    print r.headers
"""        
    

def verify_streamurl(streamurl):
    r = requests.get(streamurl, stream = True)
    content_type = r.headers["content-type"]
    if content_type == 'audio/x-mpegurl':
        content = r.raw.readlines()
        streamurls = parse_mpegurl(content)
        return streamurls[0]
    else:
        return streamurl
    
    
        
def rec_worker(stop, streamurl, outputdir):

    streamurl = verify_streamurl(streamurl)
    r = requests.get(streamurl, stream = True)
        
    channelname = r.headers["icy-name"]
    ctype = r.headers["Content-Type"]
    fsuffix = ".mp3"
    if "ogg" in ctype:
        fsuffix = ".ogg"
            
    cur_dt_string = datetime.datetime.now().strftime('%Y-%m-%dT%H_%M_%S')
    filename = os.path.join(outputdir, channelname +"_"+ cur_dt_string + fsuffix)
    
    with open(filename, "wb") as target:
        while(not stop.is_set()):
            target.write(r.raw.read(1024))
    

    

if __name__ == "__main__":
    url = "http://dradio_mp3_dwissen_m.akacast.akamaistream.net/7/728/142684/v1/gnl.akacast.akamaistream.net/dradio_mp3_dwissen_m"
    outputdir = "./output"
    duration = 1/60.0
    
    #rec(url, outputdir, duration)
    
    brklassik = "http://streams.br-online.de/br-klassik_2.m3u"
    dkultur = "http://www.deutschlandradio.de/streaming/dkultur.m3u"
    dlf = "http://www.deutschlandradio.de/streaming/dlf.m3u"
    dwissen = "http://dradio_mp3_dwissen_m.akacast.akamaistream.net/7/728/142684/v1/gnl.akacast.akamaistream.net/dradio_mp3_dwissen_m"
    erfplus = "http://c14000-l.i.core.cdn.streamfarm.net/14000cina/live/3212erf_96/live_de_96.mp3"
    mdrklassik = "http://avw.mdr.de/livestreams/mdr_klassik_live_128.m3u"
    swr2 = "http://mp3-live.swr.de/swr2_m.m3u"
    wdr3 = "http://www.wdr.de/wdrlive/media/mp3/wdr3_hq.m3u"
    urls = [brklassik, dkultur, dlf, dwissen, erfplus, mdrklassik, swr2, wdr3]
    
    #for url in urls: 
    #    rec(url, outputdir, duration)
    #future_rec(urls[0], outputdir, "", "")
    
    strtime = datetime.datetime.strptime("2016-10-13 13:00", "%Y-%m-%d %H:%M")
    endtime = datetime.datetime.strptime("2016-10-13 13:10", "%Y-%m-%d %H:%M")
    
    #timer(strtime, endtime, dlf, outputdir)
    
    
    
