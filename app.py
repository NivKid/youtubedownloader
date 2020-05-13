from flask import Flask, make_response,render_template,jsonify
from flask import render_template, request, redirect,send_from_directory
import os
import json
from hurry.filesize import size
import urllib
import xmltodict
import youtube_dl

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

def GetAudioStreamFromXML(url):
  source = urllib.request.urlopen(url)
  data = source.read()
  XMLDICT = xmltodict.parse(data)
  resolved ={}
  resolved['url'] = XMLDICT['MPD']['Period']['AdaptationSet'][0]['Representation'][1]['BaseURL']
  resolved['filesize'] = XMLDICT['MPD']['Period']['AdaptationSet'][0]['Representation'][1]['@bandwidth']
  return resolved

def VideoHTMLrender(title,videostreams,audiostreams):
    check = 0
    a= '''<html><head>
        <style>
        table {
        font-family: arial, sans-serif;
        border-collapse: collapse;
        width: 100%;
        }

        td, th {
        border: 1px solid #dddddd;
        text-align: left;
        padding: 8px;
        }

        tr:nth-child(even) {
        background-color: #dddddd;
        }
        </style>
        </head><body><h1>'''+title+'</h1>'
    for videostream in videostreams:
        if check == 0:
            a=a+'<p>VIDEO:</p>'
            a=a+'<table><tr><th>resolution</th><th>extension</th><th>filesize</th><th>DownloadLink</th></tr><tr>'
            check =1
        a=a+'<td>'+videostream['format']+'</td>'
        a=a+'<td>'+videostream['ext']+'</td>'
        a=a+'<td>'+str(size(videostream['filesize']))+'</td>'
        a=a+'<td><a href="'+videostream['url']+'">click here to download</a></td></tr>'
    a=a+'</table>'    
    check = 0
    for audiostream in audiostreams:
        if(audiostream['url'].startswith("https://manifest.googlevideo.com/api/manifest/")):
            resolved = GetAudioStreamFromXML(audiostream['url'])
            aurl = resolved['url']
            asize = resolved['filesize']
        else:
          aurl = audiostream['url']    
          asize = audiostream['filesize']
        if check == 0:
            a=a+'<p>AUDIO:</p>'
            a=a+'<table><tr><th>bitrate</th><th>extension</th><th>filesize</th><th>DownloadLink</th></tr><tr>'
            check = 1
        a=a+'<td>'+str(audiostream['abr'])+'</td>'
        a=a+'<td>'+audiostream['ext']+'</td>'
        a=a+'<td>'+str(size(int(asize)))+'</td>'
        a=a+'<td><a href="'+aurl+'">click here to download</a></td></tr>'
    a=a+'</table>'    
    a=a+'</body></html>'
    return a

# def PlaylistHTMLrender(): 


@app.route('/')
def form():
    return  """
        <html>
            <body>
                <h1>enter the youtube video link :</h1>
                <form action="/transform" method="post" enctype="multipart/form-data">
                    <input type="text" name="link" />
                    <input type="submit" />
                </form>
            </body>
        </html>
    """

@app.route('/transform', methods=["POST"])
def transform_view():
    url = request.form['link']
    print("fiels>>>" + url)

    ydl = youtube_dl.YoutubeDL()
    with ydl:
        result = ydl.extract_info( url, download=False)

    if 'entries' in result:
        # Can be a playlist or a list of videos
        title = result['title']
        videos = result['entries']
        for video in videos:
            print('##########################################')
            print(video['title'])
            media_url = video['formats']
            videostreams = []
            audiostreams = []
            for r in media_url:
                if r['acodec']!='none':
                    videostream ={}
                    audiostream ={}
                    if r['vcodec']!= 'none' :
                        videostream['url'] = r['url']
                        videostream['ext'] = r['ext']
                        videostream['filesize'] = r['filesize']
                        videostream['format'] = r['format'].split('-',1)[-1].lstrip()
                        videostreams.append(videostream)
                    else:
                        audiostream['url'] = r['url']
                        audiostream['ext'] = r['ext']
                        audiostream['filesize'] = r['filesize']
                        audiostream['abr'] = r['abr']
                        audiostreams.append(audiostream)
        # resultpage = PlaylistHTMLrender(title,videostreams,audiostreams)

    else:
        # Just a video
        title = result['title']
        media_url = result['formats']
        videostreams = []
        audiostreams = []
        for r in media_url:
            if r['acodec']!='none':
                videostream ={}
                audiostream ={}
                if r['vcodec']!= 'none' :
                    videostream['url'] = r['url']
                    videostream['ext'] = r['ext']
                    videostream['filesize'] = r['filesize']
                    videostream['format'] = r['format'].split('-',1)[-1].lstrip()
                    videostreams.append(videostream)
                else:
                    audiostream['url'] = r['url']
                    audiostream['ext'] = r['ext']
                    audiostream['filesize'] = r['filesize']
                    audiostream['abr'] = r['abr']
                    audiostreams.append(audiostream)
        resultpage = VideoHTMLrender(title,videostreams,audiostreams)

                
    return resultpage

if __name__ == "__main__":
    app.run(debug=True)    
