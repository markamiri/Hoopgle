"""
from flask import Flask, request, render_template, session, redirect, url_for
import pandas as pd
from fuzzywuzzy import fuzz, process
import requests
import numpy as np

import re
from fuzzywuzzy import process

app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route('/')
def home():
    
    return render_template('site.html')
    """