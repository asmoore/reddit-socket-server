import time
from threading import Thread
import json
from datetime import datetime, timedelta
import os
import sys

from flask import Flask, flash, render_template, session, request, redirect, url_for, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
import praw


app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
socketio = SocketIO(app)
thread = None

r = praw.Reddit(user_agent='catmoon using praw')
subreddit= 'nba'


@socketio.on('send_message')
def handle_source(json_data):
    text = json_data['message'].encode('ascii', 'ignore')
    socketio.emit('echo', {'echo': 'Server Says: '+text})


@socketio.on('join')
def join(message):
	print "someone joined"
	join_room(message['room'])
	emit('my response', {'data': 'new user entered'})


def server_backend():
    for comment in praw.helpers.comment_stream(r, subreddit):
        comment_dict = {"author": comment.author.name, 
                         "body": comment.body, 
                         "author_flair_css_class": comment.author_flair_css_class, 
                         "comment_id": comment.id, 
                         "score": comment.score,
                         "created_utc": comment.created_utc, 
                         "emitted": "false",
                         "thread_id": (comment.link_id).split("_",1)[1]}
        message = json.dumps({'message': comment_dict,'category':'comment', 'thread': 'asda'})
        socketio.emit('echo', message, room='2zeobb')


if __name__ == '__main__':
	if thread is None:
		thread = Thread(target=server_backend)
		thread.start()
	socketio.run(app)
