from flask import render_template, request, redirect, url_for, abort, flash
from . import main
from ..models import User, Role, Post, Comment
from .forms import CommentForm, PostForm
from flask_login import login_required, current_user
from datetime import datetime, timezone
from .. import db
import markdown2
from ..email import send_email
from ..requests import get_quotes


# Views
@main.route('/')
def index():
    '''
    View root page function that returns the index page and its data
    '''

    title = 'Home'
    posts = Post.get_posts()
    quote = get_quotes()

    return render_template('index.html', title=title, posts=posts, quote=quote)


@main.route('/post/<int:id>')
def post(id):
    '''
    View post page function that returns a page with a post and its comments
    '''
    post = Post.query.get(id)
    title = f'Post {post.id}'
    user = current_user

    comments = Comment.get_comments(id)

    format_post = markdown2.markdown(post.post_content, extras=["code-friendly", "fenced-code-blocks"])

    return render_template('post.html', title=title, post=post, comments=comments, format_post=format_post, user = user)


@main.route('/post/comment/new/<int:id>', methods=['GET', 'POST'])
@login_required
def new_comment(id):
    '''
    View new comment function that returns a page with a form to create a comment for the specified post
    '''
    post = Post.query.filter_by(id=id).first()

    if post is None:
        abort(404)

    form = CommentForm()

    if form.validate_on_submit():
        comment_content = form.comment_content.data
        new_comment = Comment(comment_content=comment_content, post=post)
        new_comment.save_comment()

        return redirect(url_for('.post', id=post.id))

    title = 'New Comment'
    return render_template('new_comment.html', title=title, comment_form=form)

@main.route('/writer')
@login_required
def writer():
    '''
    View root page function that returns the writer page and its data
    '''
    if current_user.role.id == 1:

        title = 'Writer'
        posts = Post.get_posts()

        return render_template('writer.html', title=title, posts=posts)

    else:
        abort(404)


@main.route('/writer/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    '''
    View new post function that returns a page with a form to create a post
    '''


    form = PostForm()

    if form.validate_on_submit():
        post_title = form.post_title.data
        post_content = form.post_content.data
        new_post = Post(post_title=post_title, post_content=post_content)
        new_post.save_post()


        return redirect(url_for('main.index'))

    title = 'Create Post'

    return render_template('new_post.html', title=title, post_form=form)




@main.route('/writer/post/<int:id>')
@login_required
def writer_post(id):
    '''
    View post page function that returns the writer page and its data
    '''
    if current_user.role.id == 1:

        post = Post.query.get(id)
        title = f'Post {post.id}'
        comments = Comment.get_comments(id)

        format_post = markdown2.markdown(post.post_content, extras=["code-friendly", "fenced-code-blocks"])

        return render_template('writer_post.html', title=title, post=post, comments=comments, format_post=format_post)

    else:
        abort(404)


@main.route('/writer/post/comment/delete/<int:id>')
@login_required
def delete_comment(id):
    '''
    View function that deletes a comment and redirect to writer view function
    '''

    if current_user.role.id == 1:

        comment = Comment.query.get(id)
        comment.delete_single_comment(id)

        return redirect(url_for('.writer'))

    else:
        abort(404)


@main.route('/writer/post/delete/<int:id>')
@login_required
def delete_post(id):
    '''
    View function that deletes a post and its comments and redirect to writer view function
    '''

    if current_user.role.id == 1:

        post = Post.query.get(id)

        post.delete_post(id)

        return redirect(url_for('.writer'))


    else:
        abort(404)


@main.route('/writer/post/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update_post(id):
    '''
    View function that updates a post and redirect to the writer view function
    '''

    if current_user.role.id == 1:

        current_post = Post.query.get(id)

        form = PostForm(obj=current_post)

        if form.validate_on_submit():
            form.populate_obj(current_post)

            comments = Comment.query.filter_by(post_id=id).all()
            post = Post.query.filter_by(id=id).update({
                'post_title': form.post_title.data,
                'post_content': form.post_content.data
            })
            db.session.commit()

            return redirect(url_for('.writer'))

        title = 'Update Post'

        return render_template('update_post.html', title=title, update_post_form=form)

    else:
        abort(404)