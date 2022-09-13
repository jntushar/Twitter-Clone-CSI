from flask import render_template, redirect, url_for, request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, current_user, login_required
from sqlalchemy import desc

from modules import app, db
from modules.modals import User_mgmt, Post, Timeline
from modules.forms import Signup, Login, createTweet

import datetime
from config import *


@app.route('/')
@app.route('/home', methods=['GET', 'POST'])
def home():
    form_sign = Signup()
    form_login = Login()

    if form_sign.validate_on_submit():
        hashed_password = generate_password_hash(form_sign.password.data, method='sha256')
        x = datetime.datetime.now()
        creation = str(x.strftime("%B")) + " " + str(x.strftime("%Y"))
        new_user = User_mgmt(username=form_sign.username.data, email=form_sign.email.data, password=hashed_password, date=creation)
        db.session.add(new_user)
        db.session.commit()
        return render_template('sign.html')

    if form_login.validate_on_submit():
        user_info = User_mgmt.query.filter_by(username=form_login.username.data).first()
        if user_info:
            if check_password_hash(user_info.password, form_login.password.data):
                login_user(user_info, remember=form_login.remember.data)
                return redirect(url_for('dashboard'))
            else:
                return render_template('errorP.html')
        else:
            return render_template('errorU.html')

    return render_template('start.html', form1=form_sign, form2=form_login)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/account')
@login_required
def account():
    profile_pic = url_for('static', filename='Images/Users/profile_pics/' + current_user.image_file)
    bg_pic = url_for('static', filename='Images/Users/bg_pics/' + current_user.bg_file)

    page = request.args.get('page', 1, type=int)
    all_posts = Post.query\
        .filter_by(user_id=current_user.id)\
        .order_by(desc(Post.id))\
        .paginate(page=page, per_page=tweets_per_page)
    return render_template('account.html', profile=profile_pic, background=bg_pic, timeline=all_posts)


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    user_tweet = createTweet()
    if user_tweet.validate_on_submit():
        x = datetime.datetime.now()
        currentTime = str(x.strftime("%d")) + " " + str(x.strftime("%B")) + "'" + str(x.strftime("%y")) + " " + str(x.strftime("%I")) + ":" + str(x.strftime("%M")) + " " + str(x.strftime("%p"))

        post = Post(tweet=user_tweet.tweet.data, stamp=currentTime, author=current_user)
        db.session.add(post)
        db.session.commit()

        to_timeline = Timeline(post_id=post.id)
        db.session.add(to_timeline)
        db.session.commit()
        return redirect(url_for('dashboard'))

    page = request.args.get('page', 1, type=int)
    timeline = Timeline.query\
        .order_by(desc(Timeline.id))\
        .paginate(page=page, per_page=tweets_per_page)
    return render_template('dashboard.html', name=current_user.username, tweet=user_tweet, timeline=timeline)


@app.route('/view_profile/<int:account_id>', methods=['GET', 'POST'])
@login_required
def viewProfile(account_id):
    if account_id == current_user.id:
        return redirect(url_for('account'))

    get_user = User_mgmt.query.filter_by(id=account_id).first()
    profile_pic = url_for('static', filename='Images/Users/profile_pics/' + get_user.image_file)
    bg_pic = url_for('static', filename='Images/Users/bg_pics/' + get_user.bg_file)

    page = request.args.get('page', 1, type=int)
    all_posts = Post.query\
        .filter_by(user_id=get_user.id)\
        .order_by(desc(Post.id))\
        .paginate(page=page, per_page=tweets_per_page)

    return render_template('view_profile.html', profile=profile_pic, background=bg_pic, timeline=all_posts, user=get_user)

