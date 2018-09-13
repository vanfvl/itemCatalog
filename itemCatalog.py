from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
# from models import Base, Category, CategoryItem, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

@app.route('/')
@app.route('/catalog')
def showCatalog():
	return 'this is all catalogs'

@app.route('/catalog/new')
def newCatalog():
	return "page for new catalog"

@app.route('/catalog/<category>/edit')
def editItem(category):
	return "page for edited category"

@app.route('/catalog/<category>/delete')
def deleteItem(category):
	return 'Page for delete route'

@app.route('/catalog/<category>/new')
def newItem(category):
	return 'page for new item route'


if __name__ == '__main__':
	app.debug = True
	app.run(host='0.0.0.0', port=5000)