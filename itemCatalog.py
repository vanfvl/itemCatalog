from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from models import Base, Category, CategoryItem
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

# Connect to Database and create database session
engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/')
@app.route('/catalog')
def showCatalog():
	categories = session.query(Category).order_by(asc(Category.name))


	return render_template('catalog.html', categories=categories)

@app.route('/catalog/new/')
def newCategory():
	return render_template('newCategory.html')

@app.route('/catalog/<category>/edit')
def editItem(category):
	return render_template('editItem.html')

@app.route('/catalog/<category>/delete')
def deleteItem(category):
	return render_template('deleteItem.html')

@app.route('/catalog/<category>/new')
def newItem(category):
	return render_template('newItem.html')


if __name__ == '__main__':
	app.debug = True
	app.run(host='0.0.0.0', port=5000)