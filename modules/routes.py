from flask import render_template, redirect, url_for, request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, current_user, login_required
from sqlalchemy import desc

from modules import app, db
from modules.modals import User_mgmt, Post, Following
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
                login_user(user_info)
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

    following_users = getFollowing(current_user.id)
    followers_user = getFollowers(current_user.id)
    all_posts = getUserPosts(current_user.id)

    return render_template('account.html', profile=profile_pic, background=bg_pic, timeline=all_posts,
                           following_users=following_users, followers_user=followers_user)


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

        return redirect(url_for('dashboard'))

    page = request.args.get('page', 1, type=int)
    child_ids = db.session.query(Following.child_id).filter_by(user_id=current_user.id).all()
    if len(child_ids) == 0:
        all_posts = Post.query \
            .order_by(desc(Post.id)) \
            .paginate(page=page, per_page=tweets_per_page)
    else:
        child_ids.append((current_user.id,))
        all_posts = db.session.query(Post)\
            .filter(Post.user_id.in_(tuple(i[0] for i in child_ids)))\
            .order_by(desc(Post.id))\
            .paginate(page=page, per_page=tweets_per_page)

    return render_template('dashboard.html', name=current_user.username, tweet=user_tweet, timeline=all_posts)


@app.route('/view_profile/<int:account_id>', methods=['GET', 'POST'])
@login_required
def viewProfile(account_id):
    if account_id == current_user.id:
        return redirect(url_for('account'))

    user, all_posts, profile_pic, bg_pic, follow, following_users, followers_user = getViewProfileDetails(account_id)
    status = 'Following' if follow > 0 else 'Follow'
    return render_template('view_profile.html', profile=profile_pic, background=bg_pic, timeline=all_posts,
                           user=user, follow_status=status, following_users=following_users,
                           followers_user=followers_user)


@app.route('/update_follow/<int:account_id>', methods=['GET', 'POST'])
@login_required
def update_follow(account_id):

    user, all_posts, profile_pic, bg_pic, follow, following_users, followers_user = getViewProfileDetails(account_id)
    if follow > 0:     # Following -> Follow
        Following.query\
            .filter_by(user_id=current_user.id)\
            .filter_by(child_id=account_id)\
            .delete()
        db.session.commit()
        status = 'Follow'
    else:             # Follow -> Following
        following_obj = Following(child_id=account_id, user_id=current_user.id)
        db.session.add(following_obj)
        db.session.commit()
        status = 'Following'

    return render_template('view_profile.html', profile=profile_pic, background=bg_pic, timeline=all_posts,
                           user=user, follow_status=status, following_users=following_users,
                           followers_user=followers_user)


def getViewProfileDetails(account_id):
    get_user = User_mgmt.query.filter_by(id=account_id).first()
    profile_pic = url_for('static', filename='Images/Users/profile_pics/' + get_user.image_file)
    bg_pic = url_for('static', filename='Images/Users/bg_pics/' + get_user.bg_file)

    following_users = getFollowing(account_id)
    followers_user = getFollowers(account_id)
    all_posts = getUserPosts(get_user.id)

    follow = Following.query \
        .filter_by(user_id=current_user.id) \
        .filter_by(child_id=account_id).count()

    return get_user, all_posts, profile_pic, bg_pic, follow, following_users, followers_user


def getUserPosts(user_id):
    page = request.args.get('page', 1, type=int)
    all_posts = Post.query \
        .filter_by(user_id=user_id) \
        .order_by(desc(Post.id)) \
        .paginate(page=page, per_page=tweets_per_page)
    return all_posts


def getFollowing(user_id):
    page = request.args.get('page', 1, type=int)
    following_ids = db.session.query(Following.child_id).filter_by(user_id=user_id).all()
    following_users = db.session.query(User_mgmt) \
        .filter(User_mgmt.id.in_(tuple(i[0] for i in following_ids))) \
        .order_by(desc(User_mgmt.id)) \
        .paginate(page=page, per_page=tweets_per_page)
    return following_users


def getFollowers(user_id):
    page = request.args.get('page', 1, type=int)
    followers_ids = db.session.query(Following.user_id).filter_by(child_id=user_id).all()
    followers_user = db.session.query(User_mgmt) \
        .filter(User_mgmt.id.in_(tuple(i[0] for i in followers_ids))) \
        .order_by(desc(User_mgmt.id)) \
        .paginate(page=page, per_page=tweets_per_page)
    return followers_user
