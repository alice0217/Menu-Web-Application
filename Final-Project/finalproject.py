from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, send_from_directory
import os
from werkzeug.utils import secure_filename
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

app = Flask(__name__)

# change changeRestaurantBackground backend

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine

app.config["IMAGE_UPLOADS"] = "//Users/iman.liu/"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/restaurants/JSON/')
def restaurantsJSON():
    DBSession = sessionmaker(bind=engine)
    session = DBSession()

    restaurants = session.query(Restaurant).all()
    return jsonify(Restaurants=[r.serialize for r in restaurants])

@app.route('/restaurants/<int:restaurant_id>/menu/JSON/')
def restaurantMenuJSON(restaurant_id):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()

    items = session.query(MenuItem).filter_by(restaurant_id=restaurant_id).all()
    return jsonify(MenuItems=[i.serialize for i in items])

@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_id>/JSON/')
def menuItemJSON(restaurant_id, menu_id):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()

    Menu_Item = session.query(MenuItem).filter_by(restaurant_id=restaurant_id, id=menu_id).first()
    return jsonify(Menu_Item=Menu_Item.serialize)

# displays all of the restaurants
@app.route('/restaurants/')
def showRestaurants():
    DBSession = sessionmaker(bind=engine)
    session = DBSession()

    restaurants = session.query(Restaurant).all()
    return render_template('restaurants.html', restaurants=restaurants)

# add a new restaurant
@app.route('/restaurants/new/', methods=['GET', 'POST'])
def newRestaurants():
    DBSession = sessionmaker(bind=engine)
    session = DBSession()

    if request.method == 'POST':
        newRestaurant = Restaurant(name=request.form['name'])
        session.add(newRestaurant)
        session.commit()
        flash("a new restaurant is added!")
        return redirect(url_for('showRestaurants'))
    else:
        return render_template('newRestaurant.html')

# edit a restaurant
@app.route('/restaurants/<int:restaurant_id>/edit/', methods=['GET', 'POST'])
def editRestaurant(restaurant_id):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    thatRestaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    if request.method == 'POST':
        thatRestaurant.name = request.form['name']
        session.add(thatRestaurant)
        session.commit()
        flash("the information about the restaurant has been updated!")
        return redirect(url_for('showRestaurants'))
    else:
        return render_template('editRestaurant.html', restaurant_id=restaurant_id, restaurant=thatRestaurant)

# delete a restaurant
@app.route('/restaurants/<int:restaurant_id>/delete/', methods=['GET', 'POST'])
def deleteRestaurant(restaurant_id):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    thatRestaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    if request.method == 'POST':
        session.delete(thatRestaurant)
        session.commit()
        flash("the restaurant is deleted!")
        return redirect(url_for('showRestaurants'))
    else:
        return render_template('deleteRestaurant.html', restaurant_id=restaurant_id, restaurant=thatRestaurant)

# send_from_directory
@app.route('/uploads/<filename>')
def send_uploaded_file(filename=''):
    from flask import send_from_directory
    return send_from_directory(app.config["IMAGE_UPLOADS"], filename)

# show the menu of a restaurant
@app.route('/restaurants/<int:restaurant_id>/menu/', methods=['GET', 'POST'])
def showMenu(restaurant_id):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()

    thatRestaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant_id).all()
    if request.method == 'POST':
        # check if the post request has the file part
        if 'background' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['background']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            background = request.files['background']
            background.save(os.path.join(app.config["IMAGE_UPLOADS"], filename))
            thatRestaurant.background = filename
            session.add(thatRestaurant)
            session.commit()
            flash('the background is changed successfully!')
            return redirect(url_for('showMenu', restaurant_id=restaurant_id))
        else:
            flash("invalid file type")
            return redirect(request.url)
    else:
        return render_template('menu.html', restaurant_id=restaurant_id, restaurant=thatRestaurant, items=items)

# add a new menu item
@app.route('/restaurants/<int:restaurant_id>/menu/new/', methods=['GET', 'POST'])
def newMenuItem(restaurant_id):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    if request.method == 'POST':
        # don't forget the restaurant id
        newItem = MenuItem(name=request.form['name'], description=request.form['description'], price=request.form['price'], course=request.form['course'], restaurant_id=restaurant_id)
        session.add(newItem)
        session.commit()
        flash("a new item is added!")
        return redirect(url_for('showMenu', restaurant_id=restaurant_id))
    else:
        return render_template('newmenuitem.html', restaurant_id=restaurant_id)

# edit a menu item
@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_id>/edit/', methods=['GET', 'POST'])
def editMenuItem(restaurant_id, menu_id):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    thatRestaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    thatItem = session.query(MenuItem).filter_by(restaurant_id=restaurant_id, id=menu_id).one()
    # the user doesn't need to retype anything if they don't want to change that
    if request.method == 'POST':
        if request.form['name']:
            thatItem.name = request.form['name']
        if request.form['description']:
            thatItem.description = request.form['description']
        if request.form['price']:
            thatItem.price = request.form['price']
        if request.form['course']:
            thatItem.course = request.form['course']
        session.add(thatItem)
        session.commit()
        flash("the information about the menu item has been updated!")
        return redirect(url_for('showMenu', restaurant_id=restaurant_id))
    else:
        return render_template('editmenuitem.html', restaurant_id=restaurant_id, menu_id=menu_id, item=thatItem, restaurant=thatRestaurant)

# delete a menu item
@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_id>/delete/', methods=['GET', 'POST'])
def deleteMenuItem(restaurant_id, menu_id):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    thatRestaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    thatItem = session.query(MenuItem).filter_by(restaurant_id=restaurant_id, id=menu_id).one()

    if request.method == 'POST':
        session.delete(thatItem)
        session.commit()
        flash("the item is deleted!")
        return redirect(url_for('showMenu', restaurant_id=restaurant_id))
    else:
        return render_template('deletemenuitem.html', restaurant_id=restaurant_id, menu_id=menu_id, item=thatItem, restaurant=thatRestaurant)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
