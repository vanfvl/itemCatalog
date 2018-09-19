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
engine = create_engine('sqlite:///itemcatalog.db?check_same_thread=False')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/')
@app.route('/catalog/')
def showCatalog():
	categories = session.query(Category).order_by(asc(Category.name))
	return render_template('catalog.html', categories=categories)

@app.route('/catalog/<category>/')
def showCategory(category):
	category = session.query(Category).filter_by(name = category).first()
	items = session.query(CategoryItem).filter_by(category = category).all()
	return render_template('items.html', items = items, category = category)

@app.route('/catalog/new/', methods=['GET', 'POST'])
def newCategory():
	if request.method == 'POST':
		newCategory = Category(name=request.form['name'])
		session.add(newCategory)
		flash('New Category %s Successfully Created' % newCategory.name)
		session.commit()
		return redirect(url_for('showCatalog'))
	else:
		return render_template('newCategory.html')

@app.route('/catalog/<category>/<item>/')
def showItem(category, item):
	category = session.query(Category).filter_by(name = category).first()
	item = session.query(CategoryItem).filter_by(name = item).one()
	return render_template('item.html', item = item, category = category)

@app.route('/catalog/<category>/<item>/edit/')
def editItem(category, item):
	category = session.query(Category).filter_by(name = category).first()
	itemEdited = session.query(CategoryItem).filter_by(name = item).one()

	return render_template('editItem.html', item = itemEdited)

@app.route('/catalog/<category>/new', methods=['GET', 'POST'])
def newItem(category):
 	category = session.query(Category).filter_by(name = category).first()
	if request.method == 'POST':
		newItem = CategoryItem(name=request.form['name'], description=request.form['description'], price=request.form['price'], 
			category=category, category_id=category.id)
		session.add(newItem)
		session.commit()
		return redirect(url_for('showCategory', category = category.name))
	else:
		return render_template('newItem.html')

@app.route('/catalog/<category>/<item>/delete', methods=['GET', 'POST'])
def deleteItem(category, item):
	category = session.query(Category).filter_by(name = category).first()
	itemToDelete = session.query(CategoryItem).filter_by(name = item).one()
	if request.method == 'POST':
		session.delete(itemToDelete)
		session.commit()
		return redirect(url_for('showCategory', category = category.name))
	else:
		return render_template('deleteItem.html', item=itemToDelete)

if __name__ == '__main__':
	app.secret_key = 'super_secret_key'
	app.debug = True
	app.run(host='0.0.0.0', port=5000)