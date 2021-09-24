from flask import Flask

app=Flask(__name__)

app.config['SECRET_KEY']="asdadvadfsdfs"      #random secret key

from gdmApp import gdm
