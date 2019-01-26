from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from models import Base, Category, CategoryItem, User
from flask import session as login_session
import random
import string
# creates a flow objectfrom clent secretes json file that stores
from oauth2client.client import flow_from_clientsecrets
# flow exchange eror catches errors
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Category Item Application"
# Connect to Database and create database session
engine = create_engine('sqlite:///itemcatalogwithusers.db?check_same_thread=False')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create a state token to prevent request fogery
# Store in login_session for later validation
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        # initiate exhange with step2 func passing one time code as input
        # exhange step 2 function of flow class, exhcages an authorization code for credentials object
        credentials = oauth_flow.step2_exchange(code)
        print 'upgraded auth code'
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        print 'there was an' + result.get('error')
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()
    print data['name']

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print login_session
    return output

# User Helper Functions


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

# DISCONNECT - Revoke a current user's token and reset their login_session


@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # google's url for revoking tokens
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        del login_session['username']
        del login_session['email']
        del login_session['provider']
        del login_session['picture']
        del login_session['gplus_id']
        flash("You have successfully been logged out.")
        return redirect(url_for('showCatalog'))
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/')
@app.route('/catalog/')
def showCatalog():
    categories = session.query(Category).order_by(asc(Category.name))
    return render_template('catalog.html', categories=categories)


@app.route('/catalog/<category>/')
def showCategory(category):
    categories = session.query(Category).all()
    category = session.query(Category).filter_by(name=category).first()
    items = session.query(CategoryItem).filter_by(category=category).all()
    return render_template('items.html', items=items, category=category, categories = categories)


@app.route('/catalog/new/', methods=['GET', 'POST'])
def newCategory():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newCategory = Category(name=request.form['name'], user_id=login_session['user_id'])
        session.add(newCategory)
        flash('New Category %s Successfully Created' % newCategory.name)
        session.commit()
        return redirect(url_for('showCatalog'))
    else:
        return render_template('newCategory.html')

@app.route('/catalog/<category>/delete', methods=['GET', 'POST'])
def deleteCategory(category):
    category = session.query(Category).filter_by(name=category).first()
    if request.method == 'POST':
        session.delete(category)
        session.commit()
        return redirect(url_for('showCatalog'))
    else:
        return render_template('deleteCategory.html', category=category)


@app.route('/catalog/<category>/<item>/')
def showItem(category, item):
    category = session.query(Category).filter_by(name=category).first()
    item = session.query(CategoryItem).filter_by(name=item).first()
    return render_template('item.html', item = item, category=category)


@app.route('/catalog/<category>/new', methods=['GET', 'POST'])
def newItem(category):
    category = session.query(Category).filter_by(name=category).first()
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newItem = CategoryItem(name=request.form['name'], description=request.form['description'], price=request.form['price'], 
        	category_id=category.id, user_id=login_session['user_id'])
        session.add(newItem)
        session.commit()
        return redirect(url_for('showCategory', category=category.name))
    else:
        return render_template('newItem.html', category=category)


@app.route('/catalog/<category>/<item>/edit/', methods=['GET', 'POST'])
def editItem(category, item):
    category = session.query(Category).filter_by(name=category).first()
    itemEdited = session.query(CategoryItem).filter_by(name=item).one()
    print category
    if 'username' not in login_session:
        return redirect('/login')

    if itemEdited.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to edit this item. ');}</script><body onload='myFunction()'>"

    if request.method == 'POST':
        if request.form['name']:
            itemEdited.name = request.form['name']
        if request.form['description']:
            itemEdited.description = request.form['description']
        if request.form['price']:
            itemEdited.price = request.form['price']
        session.add(itemEdited)
        session.commit()    
        return redirect(url_for('showCategory', category=category.name))
    else:
        return render_template('editItem.html',item=itemEdited, category=category)


@app.route('/catalog/<category>/<item>/delete', methods=['GET', 'POST'])
def deleteItem(category, item):
    category = session.query(Category).filter_by(name = category).first()
    itemToDelete = session.query(CategoryItem).filter_by(name = item).first()
    if 'username' not in login_session:
        return redirect('/login')
    if itemToDelete.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to delete this item. ');}</script><body onload='myFunction()'>"
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        return redirect(url_for('showCategory', category = category.name))
    else:
        return render_template('deleteItem.html', item=itemToDelete, category=category)


# Disconnect based on provider
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['access_token']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        # del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('showCatalog'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showCatalog'))

@app.route('/clear')
def clearLogin():
	login_session.clear()
	return 'login session cleared!'

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
