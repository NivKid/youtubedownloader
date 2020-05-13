from flask import Flask, make_response,render_template,jsonify
from flask import render_template, request, redirect,send_from_directory
import os
import json
import pafy
from hurry.filesize import size
import urllib
import xmltodict

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

def GetAudioStreamFromXML(url):
  source = urllib.request.urlopen(url)
  data = source.read()
  XMLDICT = xmltodict.parse(data)
  audiostream = XMLDICT['MPD']['Period']['AdaptationSet'][0]['Representation'][1]['BaseURL']
  return audiostream


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
    # video = YouTube(url)
    # streams = video.streams.all()
    video = pafy.new(url)
    title= video.title
    streams = video.streams
    audiostreams = video.audiostreams
    check = 0
    a= '<html><body><h1>'+title+'</h1>'
    for s in streams:
        if check == 0:
            a=a+'<p>-------------------VIDEO-----------------------</p>'
            check =1
        else:
            a=a+'<p>-----------------------------------------------</p>'
        a=a+'<p>resolution: '+s.resolution+'</p>'
        a=a+'<p>extension: '+s.extension+'</p>'
        a=a+'<p>filesize: '+str(size(s.get_filesize()))+'</p>'
        a=a+'<p>DownloadLink: <a href="'+s.url+'">click here to download</a></p>'
    check = 0
    for aus in audiostreams:
        if(aus.url.startswith("https://manifest.googlevideo.com/api/manifest/")):
            aurl = GetAudioStreamFromXML(aus.url)
        else:
          aurl = aus.url     
        if check == 0:
            a=a+'<p>-------------------AUDIO-----------------------</p>'
            check = 1
        else:
            a=a+'<p>-----------------------------------------------</p>'
        a=a+'<p>extension: '+aus.extension+'</p>'
        a=a+'<p>filesize: '+str(size(aus.get_filesize()))+'</p>'
        a=a+'<p>DownloadLink: <a href="'+aurl+'">click here to download</a></p>'
    a=a+'</body></html>'    
    return a

if __name__ == "__main__":
    app.run(debug=True)    
