
from flask import Flask, make_response,render_template,jsonify
from flask import render_template, request, redirect,send_from_directory
# from werkzeug.utils import secure_filename
import os
import json
# from pytube import YouTube
import pafy


app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

@app.route('/')
def form():
    return render_template('index.html')

@app.route('/transform', methods=["POST"])
def transform_view():
    url = request.form['link']
    print("fiels>>>" + url)
    # video = YouTube(url)
    # streams = video.streams.all()
    video = pafy.new(url)
    title= video.title
    streams = video.streams
    a= '<html><body><h1>'+title+'</h1>'
    streamslist = []
    for s in streams:
        item={}
        a=a+'<p>-----------------------------------------------</p>'
        a=a+'<p>resolution: '+s.resolution+'</p>'
        a=a+'<p>extension: '+s.extension+'</p>'
        a=a+'<p>filesize: '+str(s.get_filesize())+'</p>'
        a=a+'<p>DownloadLink: <a href="'+s.url+'">click here to download</a></p>'
    a=a+'</body></html>'    
    return a


if __name__ == "__main__":
    app.run(debug=True)    