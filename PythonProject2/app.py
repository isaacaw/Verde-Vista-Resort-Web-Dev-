import shelve
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_bcrypt import Bcrypt
import datetime
import os
import re
from werkzeug.utils import secure_filename
from flask import Flask, request, jsonify
import google.generativeai as genai

import hashlib

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Important for session management and flash messages

# Configure upload folder for room images
app.config['UPLOAD_FOLDER'] = 'static/room_images'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)  # Create folder if it doesn't exist

# Initialize Flask-Login and Bcrypt
login_manager = LoginManager(app)
login_manager.login_view = "login"
bcrypt = Bcrypt(app)


# -----------------------------------------
# SHELVE DATABASE MODELS
# -----------------------------------------

class User(UserMixin):
    def __init__(self, id, username, email, phone, password, is_admin, points_balance, membership_level=False):
        self.id = id
        self.username = username
        self.email = email
        self.phone = phone
        self.password = password
        self.is_admin = is_admin
        self.points_balance = points_balance
        self.membership_level = membership_level


# -----------------------------------------
# HELPER FUNCTIONS
# -----------------------------------------

def get_next_id(collection):
    """Generate the next ID for a given collection."""
    with shelve.open(collection) as db:
        return str(len(db) + 1)


def hash_password(password):
    """Hash password for secure storage."""
    return bcrypt.generate_password_hash(password).decode('utf-8')


def validate_password(password):
    """Validate password strength."""
    if len(password) < 8:
        return "Password must be at least 8 characters long."
    if not re.search(r"[A-Z]", password):
        return "Password must contain at least one uppercase letter."
    if not re.search(r"[a-z]", password):
        return "Password must contain at least one lowercase letter."
    if not re.search(r"\d", password):
        return "Password must contain at least one digit."
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return "Password must contain at least one special character."
    return None


def verify_password(hashed_password, password):
    """Verify a password against its hash."""
    return bcrypt.check_password_hash(hashed_password, password)


def create_hardcoded_rooms():
    """Prepopulate rooms with hardcoded data."""
    with shelve.open('rooms') as rooms_db:
        if not rooms_db:  # Only add rooms if the database is empty
            rooms_db['1'] = {
                'id': '1',
                'room_type': 'Single Room',
                'price': 600,
                'description': 'A cozy single room with a beautiful view.',
                'image': 'twin_room.jpg',
                'extra_images': ['room_image_1.jpg', 'room_image_2.jpg', 'room_image_3.jpg', 'room_image_4.jpg', 'room_image_5.jpg'],
                'amenities': [
                    'Private balcony',
                    'Individual temperature control',
                    'In-room safe',
                    'Laundry and dry cleaning services',
                    'Pillow menu',
                    'Coffee machine',
                    'Unlimited wireless Internet access',
                    'LCD TV with local and international channels'
                ]
            }
            rooms_db['2'] = {
                'id': '2',
                'room_type': 'Double Room',
                'price': 800,
                'description': 'A spacious double room for two guests.',
                'image': 'double_room.jpg',
                'extra_images': ['room_image_1.jpg', 'room_image_2.jpg', 'room_image_3.jpg', 'room_image_4.jpg', 'room_image_5.jpg'],
                'amenities': [
                    'Private balcony',
                    'Individual temperature control',
                    'In-room safe',
                    'Laundry and dry cleaning services',
                    'Pillow menu',
                    'Coffee machine',
                    'Unlimited wireless Internet access',
                    'LCD TV with local and international channels'
                ]
            }
            rooms_db['3'] = {
                'id': '3',
                'room_type': 'Suite',
                'price': 1500,
                'description': 'A luxurious suite with premium amenities.',
                'image': 'suite_room.jpg',
                'extra_images': ['room_image_7.jpg', 'room_image_8.jpg', 'room_image_9.jpg'],
                'amenities': [
                    'Private balcony',
                    'Individual temperature control',
                    'In-room safe',
                    'Laundry and dry cleaning services',
                    'Pillow menu',
                    'Coffee machine',
                    'Unlimited wireless Internet access',
                    'LCD TV with local and international channels'
                ]
            }

import uuid

def generate_booking_id():
    return 'BK-' + str(uuid.uuid4().hex)[:6].upper()

def init_rewards_db():
    with shelve.open('rewards') as rewards_db:
        if not rewards_db:
            rewards_db['admin'] = []  # Example: Admin has no rewards initially


@login_manager.user_loader
def load_user(user_id):
    """Load a user from the shelve database."""
    with shelve.open('users') as users_db:
        if user_id in users_db:
            user_data = users_db[user_id]
            return User(id=user_id, **user_data)
    return None


# -----------------------------------------
# ROUTES
# -----------------------------------------

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/room')
def room():
    create_hardcoded_rooms()  # Ensure rooms are created
    with shelve.open('rooms') as rooms_db:
        rooms = list(rooms_db.values())  # Fetch all rooms from the database
    return render_template('room.html', rooms=rooms)

@app.route('/dining')
def dining():
    return render_template('dining.html')

@app.route('/facilities')
def facilities():
    return render_template('facilities.html')


# ---------------- LOGIN / SIGNUP ----------------

def create_admin():
    with shelve.open('users') as users_db:
        # Check if the admin already exists
        if 'admin' not in users_db:
            # Hash password and store it
            hashed_password = generate_password_hash('adminpassword')
            users_db['admin'] = {
                'username': 'admin',
                'email': 'admin@admin.com',
                'phone': '1234567890',
                'password': hashed_password,  # Store the hashed password
                'is_admin': True,  # Set is_admin to True for admin
                'points_balance': 1500,  # Initialize points balance
                'membership_level': 'Gold'  # Initialize membership level
            }
            print("Admin account created successfully.")
        else:
            print("Admin account already exists.")

# Call the function to create the admin account
create_admin()


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        with shelve.open('users') as users_db:
            # Check if the entered username and password match the admin hardcoded credentials
            if username == 'admin' and check_password_hash(generate_password_hash('adminpassword'), password):
                user = User(
                    id='admin',
                    username='admin',
                    email='admin@admin.com',
                    phone='1234567890',
                    password=generate_password_hash('adminpassword'),
                    is_admin=True,
                    points_balance=1500,  # Initialize points balance
                    membership_level='Gold'  # Initialize membership level
                )
                login_user(user)
                return redirect(url_for('admin_home'))  # Redirect to admin_home.html

            # Check in the shelve database for other users
            for user_id, user_data in users_db.items():
                if user_data['username'] == username and check_password_hash(user_data['password'], password):
                    user = User(
                        id=user_id,
                        username=user_data['username'],
                        email=user_data['email'],
                        phone=user_data['phone'],
                        password=user_data['password'],
                        is_admin=user_data['is_admin'],
                        points_balance=user_data['points_balance'],  # Load points balance
                        membership_level=user_data['membership_level']  # Load membership level
                    )
                    login_user(user)
                    flash('Login successful!', 'success')
                    # Redirect based on admin status
                    if user.is_admin:
                        return redirect(url_for('admin_room'))  # Redirect to admin_home.html
                    else:
                        return redirect(url_for('home'))  # Redirect to home.html for non-admin users

        flash('Invalid username or password', 'danger')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return redirect(url_for('register'))

        with shelve.open('users') as users_db:
            # Check if username or email already exists
            for user_data in users_db.values():
                if user_data['username'] == username:
                    flash('Username already exists', 'error')
                    return redirect(url_for('register'))
                if user_data['email'] == email:
                    flash('Email already in use', 'error')
                    return redirect(url_for('register'))

            # Create a new user
            user_id = str(len(users_db) + 1)  # Generate a unique user ID
            users_db[user_id] = {
                'username': username,
                'email': email,
                'phone': phone,
                'password': generate_password_hash(password),  # Hash the password
                'is_admin': False,  # Default to False
                'points_balance': 1500,  # Initialize points balance
                'membership_level': 'Gold'  # Initialize membership level
            }

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('home'))


# ---------------- CART ----------------

@app.route('/select_room', methods=['POST'])
def select_room():
    if current_user.is_authenticated:
        user_id = str(current_user.id)
    else:
        user_id = session.get('guest_user_id')
        if not user_id:
            user_id = str(datetime.datetime.now().timestamp())
            session['guest_user_id'] = user_id

    room_id = request.form['room_id']
    check_in_date = request.form['check_in_date']
    check_out_date = request.form['check_out_date']

    with shelve.open('rooms') as rooms_db:
        if room_id not in rooms_db:
            flash('Room not found', 'danger')
            return redirect(url_for('home'))

        room = rooms_db[room_id]

        # Ensure the room has an image (if not, use a default one)
        room_image = room.get('image', 'default_room_image.jpg')  # Replace with your default image

    num_nights = (datetime.datetime.strptime(check_out_date, '%Y-%m-%d') - datetime.datetime.strptime(check_in_date,
                                                                                                      '%Y-%m-%d')).days

    with shelve.open('carts') as carts_db:
        user_cart = carts_db.get(user_id, [])
        user_cart.append({
            'room_id': room_id,
            'room_type': room['room_type'],
            'price': room['price'],
            'description': room['description'],
            'check_in_date': check_in_date,
            'check_out_date': check_out_date,
            'quantity': 1,  # Set default quantity to 1
            'total_price': room['price'] * num_nights * 1,  # Calculate total price with quantity
            'image': room_image  # Ensure image is included in the cart item
        })
        carts_db[user_id] = user_cart

    flash('Room added to cart!', 'success')
    return redirect(url_for('view_cart'))

@app.route('/view_cart')
def view_cart():
    user_id = str(current_user.id) if current_user.is_authenticated else session.get('guest_user_id')

    if not user_id:
        user_id = str(datetime.datetime.now().timestamp())
        session['guest_user_id'] = user_id

    with shelve.open('carts') as carts_db:
        user_cart = carts_db.get(user_id, [])

    redeemed_rewards = []
    total_discount = 0
    with shelve.open('rewards') as rewards_db:
        if user_id in rewards_db:
            redeemed_rewards = rewards_db[user_id]
            total_discount = sum(reward.get('discount_amount', 0) for reward in redeemed_rewards)

            # Debugging Log
            print(f"🛒 Redeemed Rewards Data: {redeemed_rewards}")

            # Ensure no None values for offer_title
            for reward in redeemed_rewards:
                if not reward.get('offer_title'):
                    reward['offer_title'] = "Reward"

    total_price = sum(item.get('total_price', 0) for item in user_cart) - total_discount

    return render_template(
        'cart.html',
        cart_items=user_cart,
        redeemed_rewards=redeemed_rewards,
        total_price=max(0, total_price),
        total_discount=total_discount
    )


@app.route('/remove_from_cart/<int:index>')
def remove_from_cart(index):
    if current_user.is_authenticated:
        user_id = str(current_user.id)
    else:
        user_id = session.get('guest_user_id')
        if not user_id:
            user_id = str(datetime.datetime.now().timestamp())
            session['guest_user_id'] = user_id

    with shelve.open('carts') as carts_db:
        user_cart = carts_db.get(user_id, [])
        if 0 <= index < len(user_cart):
            user_cart.pop(index)
            carts_db[user_id] = user_cart
            flash('Item removed from cart!', 'success')
        else:
            flash('Invalid item index', 'error')

    return redirect(url_for('view_cart'))

@app.route('/edit_cart/<int:index>', methods=['GET', 'POST'])
def edit_cart(index):
    if current_user.is_authenticated:
        user_id = str(current_user.id)
    else:
        user_id = session.get('guest_user_id')
        if not user_id:
            user_id = str(datetime.datetime.now().timestamp())
            session['guest_user_id'] = user_id

    with shelve.open('carts') as carts_db:
        user_cart = carts_db.get(user_id, [])
        if not (0 <= index < len(user_cart)):
            flash('Invalid cart item', 'danger')
            return redirect(url_for('view_cart'))

        cart_item = user_cart[index]

    if request.method == 'POST':
        check_in_date = request.form['check_in_date']
        check_out_date = request.form['check_out_date']
        quantity = int(request.form.get('quantity', 1))

        num_nights = (datetime.datetime.strptime(check_out_date, '%Y-%m-%d') - datetime.datetime.strptime(check_in_date, '%Y-%m-%d')).days

        cart_item['check_in_date'] = check_in_date
        cart_item['check_out_date'] = check_out_date
        cart_item['quantity'] = quantity
        cart_item['total_price'] = cart_item['price'] * num_nights * quantity

        with shelve.open('carts') as carts_db:
            user_cart[index] = cart_item
            carts_db[user_id] = user_cart

        flash('Cart updated successfully!', 'success')
        return redirect(url_for('view_cart'))

    return render_template('edit_cart.html', cart_item=cart_item)

@app.route('/payment', methods=['GET', 'POST'])
def payment():
    user_id = str(current_user.id) if current_user.is_authenticated else session.get('guest_user_id')

    if not user_id:
        user_id = str(datetime.datetime.now().timestamp())
        session['guest_user_id'] = user_id

    with shelve.open('carts') as carts_db:
        user_cart = carts_db.get(user_id, [])

    redeemed_rewards = []
    total_discount = 0
    with shelve.open('rewards') as rewards_db:
        if user_id in rewards_db:
            redeemed_rewards = rewards_db[user_id]
            total_discount = sum(reward.get('discount_amount', 0) for reward in redeemed_rewards)

            for reward in redeemed_rewards:
                if not reward.get('offer_title'):
                    reward['offer_title'] = "Reward"

    total_price = sum(item.get('total_price', 0) for item in user_cart) - total_discount

    if request.method == 'POST':
        # Process payment and save booking details
        payment_method = request.form.get('payment-method')
        # Here you would typically process the payment with a payment gateway

        # Save booking details
        booking_details = {
            'booking_id': generate_booking_id(),  # Implement this function to generate a unique ID
            'user_id': user_id,
            'cart_items': user_cart,
            'redeemed_rewards': redeemed_rewards,
            'total_price': total_price,
            'payment_method': payment_method,
            'booking_date': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        with shelve.open('bookings') as bookings_db:
            bookings_db[booking_details['booking_id']] = booking_details

        flash('Payment successful! Your booking has been confirmed.', 'success')
        return redirect(url_for('room_booking'))

    return render_template(
        'payment.html',
        cart_items=user_cart,
        redeemed_rewards=redeemed_rewards,
        total_price=max(0, total_price),
        total_discount=total_discount
    )

# ---------------- ADMIN --------------------------------

@app.route('/admin_home')
@login_required  # Ensure only logged-in users can access this page
def admin_home():
    if not current_user.is_admin:  # Ensure only admins can access this page
        return redirect(url_for('home'))
    return render_template('admin_home.html')

@app.route('/admin_checkin')
def admin_checkin():
    return render_template('admin_checkin.html')

@app.route('/admin_checkout')
def admin_checkout():
    return render_template('admin_checkout.html')

# ---------------- ADMIN ROOM MANAGEMENT ----------------
@app.route('/add_room', methods=['POST'])
def add_room():
    room_type = request.form['room_type']
    price = float(request.form['price'])
    description = request.form['description']
    image = request.form['image']
    amenities = request.form['amenities'].split(',')

    with shelve.open('rooms') as rooms_db:
        room_id = str(max(map(int, rooms_db.keys()), default=0) + 1)  # Generate new room ID
        rooms_db[room_id] = {
            'id': room_id,
            'room_type': room_type,
            'price': price,
            'description': description,
            'image': image,
            'amenities': amenities
        }

    return redirect(url_for('room_management'))

# Edit Room
@app.route('/edit_room', methods=['POST'])
def edit_room():
    room_id = request.form['room_id']
    room_type = request.form['room_type']
    price = float(request.form['price'])
    description = request.form['description']
    image = request.form['image']
    amenities = request.form['amenities'].split(',')

    with shelve.open('rooms') as rooms_db:
        if room_id in rooms_db:
            rooms_db[room_id] = {
                'id': room_id,
                'room_type': room_type,
                'price': price,
                'description': description,
                'image': image,
                'amenities': amenities
            }

    return redirect(url_for('room_management'))

# Delete Room
@app.route('/delete_room/<room_id>', methods=['DELETE'])
def delete_room(room_id):
    with shelve.open('rooms') as rooms_db:
        if room_id in rooms_db:
            del rooms_db[room_id]
    return '', 204  # No content response

# Room Management Page
@app.route('/room_management')
def room_management():
    with shelve.open('rooms') as rooms_db:
        return render_template('room_management.html', rooms_db=rooms_db)

# -----------------------------------------
@app.route('/guest_management')
@login_required
def guest_management():
    if not current_user.is_admin:
        flash("You do not have permission to access this page.", "danger")
        return redirect(url_for('home'))

    with shelve.open('users') as users_db:
        # Ensure each user has a unique ID
        users_data = {user_id: user_data for user_id, user_data in users_db.items()}
        print(users_data)  # Debugging
        return render_template('guest_management.html', users_db=users_data)

@app.route('/amenities-management')
def amenities_management():
    return render_template('amenities_management.html')

@app.route('/room_booking')
def room_booking():
    user_id = str(current_user.id) if current_user.is_authenticated else session.get('guest_user_id')

    if not user_id:
        return redirect(url_for('login'))

    with shelve.open('bookings') as bookings_db:
        user_bookings = [booking for booking in bookings_db.values() if booking['user_id'] == user_id]

    return render_template('room_booking.html', bookings=user_bookings)



# ---------------- REVIEWS ----------------

@app.route('/review', methods=['GET'])
def review():
    try:
        with shelve.open('reviews.db') as db:
            reviews = dict(db.get('reviews', {}))
        return render_template('review.html', reviews=reviews)
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')
        return render_template('review.html', reviews={})


@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_review():
    if request.method == 'POST':
        name = request.form['name']
        review_content = request.form['review']
        rating = request.form['rating']

        if not name or not review_content or not rating:
            flash('All fields are required!', 'error')
            return redirect(url_for('add_review'))

        try:
            with shelve.open('reviews.db', writeback=True) as db:
                reviews = db.get('reviews', {})
                review_id = max(reviews.keys(), default=0) + 1  # Generate a new unique ID
                reviews[review_id] = {
                    'id': review_id,
                    'user_id': current_user.id,
                    'name': name,  # Store the name
                    'review': review_content,
                    'rating': int(rating)
                }
                db['reviews'] = reviews

            flash('Review added successfully!', 'success')
            return redirect(url_for('review'))
        except Exception as e:
            flash(f'An error occurred while adding the review: {str(e)}', 'error')
            return redirect(url_for('add_review'))

    return render_template('add_review.html')


@app.route('/edit/<int:review_id>', methods=['GET', 'POST'])
@login_required
def edit_review(review_id):
    try:
        with shelve.open('reviews.db', writeback=True) as db:
            reviews = db.get('reviews', {})

            if review_id not in reviews:
                flash('Review not found!', 'error')
                return redirect(url_for('review'))

            review = reviews[review_id]

            if review['user_id'] != current_user.id:
                flash('You can only edit your own reviews!', 'error')
                return redirect(url_for('review'))

            if request.method == 'POST':
                name = request.form['name']
                review_content = request.form['review']
                rating = request.form['rating']

                if not name or not review_content or not rating:
                    flash('All fields are required!', 'error')
                    return redirect(url_for('edit_review', review_id=review_id))

                review['name'] = name  # Update name
                review['review'] = review_content
                review['rating'] = int(rating)
                db['reviews'] = reviews

                flash('Review updated successfully!', 'success')
                return redirect(url_for('review'))

        return render_template('edit_review.html', review=review, review_id=review_id)
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')
        return redirect(url_for('review'))


@app.route('/delete/<int:review_id>', methods=['POST'])
@login_required
def delete_review(review_id):
    try:
        with shelve.open('reviews.db', writeback=True) as db:
            reviews = db.get('reviews', {})

            if review_id in reviews:
                del reviews[review_id]
                db['reviews'] = reviews
                flash('Review deleted successfully!', 'success')
            else:
                flash('Review not found!', 'error')

        return redirect(url_for('review'))
    except Exception as e:
        flash(f'An error occurred while deleting the review: {str(e)}', 'error')
        return redirect(url_for('review'))

# -----------------------------------------

genai.configure(api_key="AIzaSyAYuBkoLr1n4kgrD4kBlAn9e4hR3Wl8icU")

@app.route('/chatbot_api', methods=['POST'])
def chatbot_api():
    data = request.get_json()
    user_message = data.get("message", "")

    if not user_message:
        return jsonify({"reply": "Please ask a question."})

    # Fetch room data from the database
    with shelve.open('rooms') as rooms_db:
        rooms = list(rooms_db.values())
        room_details = "\n".join([
            f"{room['room_type']}: ${room['price']} per night"
            for room in rooms
        ])

        # Prepare amenities details
        amenities = set()  # Use a set to avoid duplicate amenities
        for room in rooms:
            amenities.update(room.get('amenities', []))
        amenities_details = "\n".join(amenities)

    # Generate AI response based on user's question
    model = genai.GenerativeModel("gemini-pro")

    if "how much" in user_message.lower() or "price" in user_message.lower():
        # Answer about room prices
        prompt = f"The user asked: '{user_message}'. Here are the room prices:\n{room_details}\nProvide a helpful response."
    elif "amenities" in user_message.lower() or "facilities" in user_message.lower():
        # Answer about amenities
        prompt = f"The user asked: '{user_message}'. Here are the available amenities:\n{amenities_details}\nProvide a helpful response."
    else:
        # For other questions, use the AI model directly
        prompt = user_message

    response = model.generate_content(prompt)
    return jsonify({"reply": response.text.strip()})

# ---------------- REWARDS ----------------

@app.route('/rewards')
@login_required
def rewards():
    user_id = current_user.id
    with shelve.open('users') as users_db:
        user_data = users_db[user_id]
        points_balance = user_data['points_balance']
        membership_level = user_data['membership_level']

    # Level Thresholds (Example)
    level_thresholds = {
        "Bronze": 0,
        "Silver": 1000,
        "Gold": 1500,
        "Platinum": 2000
    }
    max_points = level_thresholds["Platinum"]  # Assuming Platinum is the max level

    # Calculate Progress
    progress = points_balance / max_points
    progress = min(progress, 1)  # Ensure progress doesn't exceed 1 (100%)
    progress_offset = 314 * (1 - progress)  # Calculate the dash offset

    offers = [
        {"id": 1, "title": "$5.00 Off Dining", "points": 500},
        {"id": 2, "title": "$5.00 Off Your Stay", "points": 750},
        {"id": 3, "title": "$10.00 Off Dining", "points": 1000},
        {"id": 4, "title": "$10.00 Off Your Stay", "points": 1500}
    ]

    return render_template(
        'rewards.html',
        points_balance=points_balance,
        offers=offers,
        membership_level=membership_level,
        progress_offset=progress_offset
    )


@app.route('/redeem', methods=['POST'])
@login_required
def redeem():
    user_id = str(current_user.id)
    data = request.get_json()
    offer_id = int(data.get('offer_id'))
    offer_points = int(data.get('offer_points'))
    offer_title = data.get('offer_title', '').strip()  # Ensure it's a string and strip spaces

    # Debugging Log
    print(f"🔍 Redeeming Offer: ID={offer_id}, Title='{offer_title}', Points={offer_points}")

    # Define discount mapping
    discount_mapping = {
        2: 5.00,   # "$5.00 Off Your Stay"
        4: 10.00   # "$10.00 Off Your Stay"
    }
    discount_amount = discount_mapping.get(offer_id, 0)

    with shelve.open('users') as users_db, shelve.open('rewards', writeback=True) as rewards_db:
        user_data = users_db[user_id]
        points_balance = user_data['points_balance']

        if points_balance >= offer_points:
            points_balance -= offer_points
            user_data['points_balance'] = points_balance
            users_db[user_id] = user_data

            # Ensure user entry exists in rewards_db
            if user_id not in rewards_db:
                rewards_db[user_id] = []

            # Append the reward with a valid title
            rewards_db[user_id].append({
                'offer_id': offer_id,
                'offer_title': offer_title if offer_title else "Reward",  # Fallback
                'offer_points': offer_points,
                'discount_amount': discount_amount
            })
            rewards_db.sync()  # Save changes

            print(f"✅ Reward Redeemed: {rewards_db[user_id]}")  # Debugging log

            return jsonify({
                'success': True,
                'new_balance': points_balance,
                'discount_applied': discount_amount,
                'message': 'Reward redeemed successfully!'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Insufficient points'
            })


# -----------------------------------------
# RUN THE APPLICATION
# -----------------------------------------

if __name__ == '__main__':
    app.run(debug=True)