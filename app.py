from flask import Flask, render_template, url_for, request, redirect, jsonify
from flask import flash, make_response
from flask import session as login_session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, ForeignKey, Integer, String
from database import Base, User, Category, Item
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import random
import string
import httplib2
import json
import requests

# Instantiate App
app = Flask(__name__)

# Read Google client_secrets.json and assign client_id for later use.
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Catalog Application"

# Connect to database and initiate session.
engine = create_engine('sqlite:///catalog.db',
                       connect_args={'check_same_thread': False})
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/login')
def showLogin():
    """ Create anti-forgery state token and present login interface """

    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    """ Handles a user authorization request from Google Sign-in API. """

    # Validate state token
    if request.args.get('state') != login_session['state']:
        arg_state = request.args.get('state')
        login_state = login_session['state']
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
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
        return response

    # Verify that the access token is used for the intended user.
    google_id = credentials.id_token['sub']
    if result['user_id'] != google_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        print("Token's user ID doesn't match given user ID")
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        print("Token's client ID doesn't match given user ID")
        return response

    stored_access_token = login_session.get('access_token')
    stored_google_id = login_session.get('google_id')
    if stored_access_token is not None and google_id == stored_google_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['google_id'] = google_id

    # Get user info.
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    # Assing Email as name if User does not have Google+
    if "name" in data:
        login_session['username'] = data['name']
    else:
        name = data['email'][:data['email'].find("@")]
        login_session['username'] = name_corp

    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # See if the user exists. If it doesn't, make a new one.
    user_id = get_user_id(data["email"])
    if not user_id:
        user_id = create_user(login_session)
    login_session['user_id'] = user_id
    print('Printing user id: %s' % user_id)

    # Show a welcome screen upon successful login.
    output = ''
    output += '<h2>Welcome, '
    output += login_session['username']
    output += '!</h2>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px; '
    output += 'border-radius: 150px;'
    output += '-webkit-border-radius: 150px;-moz-border-radius: 150px;">'
    flash("You are now logged in as %s!" % login_session['username'])
    print("Done!")
    return output


def create_user(login_session):
    """Create a new user.

    Argument:
    login_session (dict): The login session.
    """

    new_user = User(
        name=login_session['username'],
        email=login_session['email'],
        picture=login_session['picture']
    )
    session.add(new_user)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def get_user_info(user_id):
    """Get user information by ID.

    Argument:
        user_id (int): The user ID.

    Returns:
        The user's details.
    """

    user = session.query(User).filter_by(id=user_id).one()
    return user


def get_user_id(email):
    """Get user ID by email.

    Argument:
        email (str) : the email of the user.
    """

    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


@app.route('/logout')
def gdisconnect():
    """Disconnect the Google account of the current logged-in user."""

    # Only disconnect the connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    access_token = login_session.get('access_token')

    requests.post('https://accounts.google.com/o/oauth2/revoke',
                  params={'token': access_token},
                  headers={'content-type':
                           'application/x-www-form-urlencoded'})

    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        del login_session['access_token']
        del login_session['google_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(
            json.dumps('Failed to access token.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response


# This page will show all catalog categories and latest items
@app.route('/')
@app.route('/home')
@app.route('/catalog/')
def showCatalog():
    """
    Presents view home page view, presenting list of
    recent items and a category sidebar
    """

    categories = getCategories()
    items = session.query(Item).all()
    return render_template('catalog.html', items=items,
                           navCategories=categories)


# This page will show all catalog items for a specific category
@app.route('/catalog/<int:category_id>/')
def showCategory(category_id):
    """
    Presents view for specific category, referenced by category_id.

    Argument:
        category_id (int) : The ID of the category to display
    """

    return render_template('category.html',
                           category=getCategory(category_id),
                           items=getItems(category_id),
                           navCategories=getCategories())


# This page will show a specific catalog item
@app.route('/catalog/item/<int:item_id>/')
def showItem(item_id):
    """
    Presents view for displaying a specific catalog item, sorted by item_id.

    Argument:
        item_id (int) : The item ID of the item to display,
    """

    if item_exists(item_id):
        item = getItem(item_id)
        category_id = getCategoryID(item_id)

        if 'user_id' not in login_session:
            return render_template('item.html',
                                   category=getCategory(category_id),
                                   item=getItem(item_id))

        else:
            return render_template('item.html',
                                   category=getCategory(category_id),
                                   item=getItem(item_id),
                                   user_id=login_session['user_id'])

    else:
        flash('Something went wrong with your request :(')
        return redirect(url_for('showCatalog'))


# This page will show a form to create a new item in a category
@app.route('/catalog/<int:category_id>/new/', methods=['GET', 'POST'])
def newItem(category_id):
    """
    Provides a form interface for creating a new database item,
    and handles form submissions.

    Argument:
        category_id (int) : The category ID of the new item
    """

    if 'user_id' not in login_session:
        flash("Please log in to continue")
        return redirect(url_for('showLogin'))
    elif request.method == 'POST':
        newItem = Item(name=request.form['name'],
                       description=request.form['description'],
                       category_id=category_id,
                       user_id=login_session['user_id'])
        updateDB(newItem)
        return redirect(url_for('showCategory', category_id=category_id))
    else:
        categories = getCategories()
        return render_template('newitem.html',
                               category=getCategory(category_id),
                               categories=categories)


# This page will provide a form to edit an existing item
@app.route('/catalog/<int:category_id>/<int:item_id>/edit/',
           methods=['GET', 'POST'])
def editItem(category_id, item_id):
    """
    Provides a form interface for editing an item, and handles
    form submissions.

    Arguments:
        item_id (int) : The item ID of the item to edit,
        category_id (int) : The category ID of the item to edit
    """

    item = getItem(item_id)

    if 'user_id' not in login_session:
        print("You dont have permission to edit this item")
        flash("Please log in to continue")
        return redirect(url_for('showLogin'))

    elif item.user_id != login_session['user_id']:
        print("You don't have permission to edit this item")
        flash("You don't have permission to edit this item")
        return redirect(url_for('showItem', item_id=item_id))

    elif request.method == 'POST':

        if request.form['name']:
            item.name = request.form['name']
        if request.form['description']:
            item.description = request.form['description']
        if request.form['category']:
            item.category_id = request.form['category']

        updateDB(item)
        return redirect(url_for('showItem', item_id=item_id))

    else:
        return render_template('edititem.html',
                               categories=getCategories(),
                               item=item)


# This page will provide a form to delete an existing item
@app.route('/catalog/<int:category_id>/<int:item_id>/delete/',
           methods=['GET', 'POST'])
def deleteItem(category_id, item_id):
    """
    Provides a form interface for deleting an item, and handles
    form submissions.

    Arguments:
        item_id (int) : The item ID of the item to delete,
        category_id (int) : The category ID of the item to delete

    """

    if 'user_id' not in login_session:
        flash("Please log in to continue")
        return redirect(url_for('showLogin'))

    item = getItem(item_id)

    if item.user_id != login_session['user_id']:
        flash("You don't have permission to delete this item")
        return redirect(url_for('showItem', item_id=item_id))

    elif request.method == 'POST':
        deleteItem(item)
        return redirect(url_for('showCategory', category_id=category_id))
    else:
        return render_template('deleteitem.html',
                               category=getCategory(category_id),
                               item=getItem(item_id))


# JSON Endpoints

# Return JSON of all the items in the catalog.
@app.route('/api/catalog.json')
def show_catalog_json():
    """Return JSON of all the items in the catalog."""

    items = session.query(Item).order_by(Item.id.desc())
    return jsonify(catalog=[i.serialize for i in items])


# Return JSON of a particular item in the catalog.
@app.route(
    '/api/categories/<int:category_id>/item/<int:item_id>.json')
def catalog_item_json(category_id, item_id):
    """Return JSON of a particular item in the catalog."""

    if category_exists(category_id) and item_exists(item_id):
        item = session.query(Item)\
            .filter_by(id=item_id, category_id=category_id).first()
        if item is not None:
            return jsonify(item=item.serialize)
        else:
            return jsonify(
                error='item {} does not belong to category {}.'
                .format(item_id, category_id))
    else:
        return jsonify(error='That item or the category does not exist.')


# Return JSON of all the categories in the catalog.
@app.route('/api/categories.json')
def categories_json():
    """Returns JSON of all the categories in the catalog."""

    categories = session.query(Category).all()
    return jsonify(categories=[i.serialize for i in categories])


# Database Methods
def getCategory(category_id):
    """View an item by its ID."""

    return session.query(Category).filter_by(id=category_id).first()


def getItem(item_id):
    """View an item by its ID."""

    return session.query(Item).filter_by(id=item_id).one()


def getItems(category_id):
    """View an item by its ID."""

    return session.query(Item).filter_by(category_id=category_id).all()


def getRecentItems():
    """Get list of most recent items from database."""

    return session.query(Item).filter_by(category_id=category_id).all()


def getCategories():
    """Get a list of all categories from the database."""

    categories = session.query(Category)
    return categories


def getCategoryID(item_id):
    """Get corresponding category ID from an item.

    Argument:
        item_id (int) : The item ID to find in the database.

    Returns:
        An int value representing a unique category id.
    """

    item = getItem(item_id)
    category_id = item.category_id
    return category_id


def updateDB(item):
    """Add and commit a DB item to the current session.

    Argument:
        item (database_setup.Object) : A database item to add and commit
    """

    session.add(item)
    session.commit()


def deleteItem(item):
    """Delete Database Object and commit changes

    Argument:
        item (database_setup.Object) : A database item to add and commit
    """

    session.delete(item)
    session.commit()


# Check if the category exists in the database.
def category_exists(category_id):
    """Check if the category exists in the database.

    Argument:
        category_id (int) : The Category ID to find in the database.

    Returns:
        A boolean vale indicating whether the category exists or not.
    """

    category = session.query(Category).filter_by(id=category_id).first()
    if category is not None:
        return True
    else:
        return False


# Check if the item exists in the database,
def item_exists(item_id):
    """Check if the item exists in the database.

    Argument:
        item_id (int) : The item ID to find in the database.

    Returns:
        A boolean value indicating whether the item exists or not.
    """

    item = session.query(Item).filter_by(id=item_id).first()
    if item is not None:
        return True
    else:
        return False


if __name__ == "__main__":
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
