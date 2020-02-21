from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, request, url_for
from flask_login import UserMixin
from . import db, login_manager

class Role(db.Model):
    '''
    Role class to define a User's role in the database
    '''
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return f'User {self.name}'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    avatar_hash = db.Column(db.String(32))
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

class Post(db.Model):
    '''
    Post class to define a blog post by a user with Writer role
    '''

    # Name of the table
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key = True)
    post_title = db.Column(db.String)
    post_content = db.Column(db.String)
    post_date = db.Column(db.DateTime, default=datetime.now())
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    comments = db.relationship('Comment', backref='post', lazy='dynamic', cascade="all, delete-orphan")

    def save_post(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def get_posts(cls):
        posts = Post.query.order_by(Post.id.desc()).all()
        return posts

    @classmethod
    def delete_post(cls,post_id):
        comments = Comment.query.filter_by(post_id=post_id).delete()
        post = Post.query.filter_by(id=post_id).delete()
        db.session.commit()

class Comment(db.Model):
    '''
    Comment class to define the feedback from users
    '''
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key = True)
    comment_content = db.Column(db.String)
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id",ondelete='CASCADE') )
    user_id = db.Column(db.Integer, db.ForeignKey("users.id") )

    def save_comment(self):
        '''
        Function that saves a new comment given as feedback to a post
        '''
        db.session.add(self)
        db.session.commit()

    @classmethod
    def get_comments(cls,post_id):
        '''
        Function that queries the Comments Table in the database and returns only information with the specified post id
        Args:
            post_id : specific post_id
        Returns:
            comments : all the information for comments with the specific post id
        '''
        comments = Comment.query.filter_by(post_id=post_id).all()

        return comments

    @classmethod
    def delete_single_comment(cls,comment_id):
        '''
        Function that deletes a specific single comment from the comments table and database
        Args:
            comment_id : specific comment id
        '''
        comment = Comment.query.filter_by(id=comment_id).delete()
        db.session.commit()

class Quotes():
    '''
    Class that defines quotes received from API
    '''
    def __init__(self,id,author,quote):
        self.id = id
        self.author = author
        self.quote = quote