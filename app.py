import os
from flask import Flask, render_template, redirect, request, url_for, flash
from flask_sqlalchemy import SQLAlchemy

from models import User, Post
# from flask_login import LoginManager, current_user, login_user, UserMixin

from models import login_manager

# from flask_migrate import Migrate

from datetime import datetime
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

from flask import session
from flask_wtf.csrf import CSRFProtect
from forms import RegisterForm, LoginForm, PostForm, EditForm
from models import db
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shoppingmall.sqlite3'
app.config['SECRET_KEY'] = "software engineering"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['UPLOAD_FOLDER'] = '/Users/limhyobin/Workspace/flask_shoppingmall/static/img/'



db.init_app(app)
db.app=app

# login_manager = LoginManager(app)
# login_manager.login_view = 'auth.login'

# login_manager.init_app(app)
# csrf = CSRFProtect()
# csrf.init_app(app)


@app.route('/')
def hello():
    posts = Post.query.all()
    return render_template('mainpage.html', posts=posts)

@app.route('/testpage')
def testpage():
    users = User.query.all()
    posts = Post.query.all()
    print(posts)
    return render_template('testpage.html', users = users, posts=posts)


@app.route('/mainpage', methods = ['GET', 'POST'])
def mainpage():
    userid = session.get('userid', None)
    posts = Post.query.all()
    return render_template('mainpage.html', userid=userid, posts=posts)


@app.route('/mypage', methods = ['GET', 'POST'])
def mypage():
    # userid = session.get('userid', None)
    # author = User.query.filter_by(userid=userid).first()
    # posts = Post.query.all()
    # posts = Post.query.filter_by(post.author.userid=userid)
    # print(posts)
    # p = Post.author
    # print(p, type(p))
    # posts2 = User.posts
    # print(posts2)
    # Post.query.filter(p.userid = userid)
    userid = session['userid']
    author = User.query.filter_by(userid=userid).first()
    posts = Post.query.filter_by(user_id = author.id)

    return render_template('mypage.html', title = 'mypage', userid=userid, posts=posts, author=author)


@app.route('/registration', methods = ['GET', 'POST'])
def registration():
    # form 관리 - WTF 패키지 이용
    form = RegisterForm()
    if form.validate_on_submit(): # 내용이 채워지지 않은 항목이 있는지 체크
        
        userid = form.data.get('userid')
        username = form.data.get('username')
        email = form.data.get('email')
        password = form.data.get('password')

        usertable = User(userid, username, email, password)

        db.session.add(usertable)
        db.session.commit()

        return redirect('/login')

    return render_template('registration.html', form=form)
    # if request.method == 'GET':
    #     return render_template("registration.html")
    # else:
    #     userid = request.form.get('userid')
    #     username = request.form.get('username')
    #     email = request.form.get('email')
    #     password = request.form.get('password')
    #     password2 = request.form.get('re_password')

    #     if not (userid and email and password and password2):
    #         return "입력되지 않은 정보가 있습니다."
    #     elif password != password2:
    #         return "비밀번호가 일치하지 않습니다."
    #     else:
    #         usertable = User(userid, username, email, password)
    #         db.session.add(usertable)
    #         db.session.commit()
    #         return "회원가입 완료"
    #     return redirect('/')

@app.route('/login', methods = ['GET', 'POST'])
def login():
    # if current_user.is_authenticated:
    #     return redirect('mainpage')
    form = LoginForm() # 로그인폼
    if form.validate_on_submit():
        error = None
        usertable = User.query.filter_by(userid=form.userid.data).first()
        if not usertable:
            error = "존재하지 않는 사용자입니다."
        elif not check_password_hash(usertable.password, form.password.data):
            error = "비밀번호가 올바르지 않습니다."
        if error is None:
            session.clear()
            session['userid'] = form.data.get('userid') # form에서 가져온 userid를 세션에 저장
            return redirect('/mainpage')
        flash(error)

        # print('{} 로그인' .format(form.data.get('userid')))
        # session['userid'] = form.data.get('userid') # form에서 가져온 userid를 세션에 저장
        # return redirect('/mainpage')
    return render_template('login.html', form=form)

# def login():
#     form = LoginForm() # 로그인폼
#     if form.validate_on_submit() or request.method == 'POST':
#         error = None
#         usertable = User.query.filter_by(userid=form.userid.data).first()
#         if not usertable:
#             error = "존재하지 않는 사용자입니다."
#         elif not check_password_hash(usertable.password, form.password.data):
#             error = "비밀번호가 올바르지 않습니다."
#         if error is None:
#             session.clear()
#             session['userid'] = form.data.get('userid') # form에서 가져온 userid를 세션에 저장
#             return redirect('/mainpage')
#         flash(error)

#         # print('{} 로그인' .format(form.data.get('userid')))
#         # session['userid'] = form.data.get('userid') # form에서 가져온 userid를 세션에 저장
#         # return redirect('/mainpage')
#     return render_template('login.html', form=form)

@app.route('/logout', methods = ['GET', 'POST'])
def logout():
    session.pop('userid', None)
    return redirect('/mainpage')


@app.route('/upload_product', methods = ['GET', 'POST'])
def upload_product():
    form = PostForm()
    if form.validate_on_submit():

        keyword = form.data.get('keyword')
        content = form.data.get('content')
        price = form.data.get('price')
        userid = session['userid']
        author = User.query.filter_by(userid=userid).first()
        # print(author)
        # print(author.username)
        # print(type(author))

        # f = request.files['image']
        # f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))
        # print(f.filename)
        # imagepath = app.config['UPLOAD_FOLDER'] + f.filename
        # print(imagepath)

        posttable = Post(keyword=keyword, content=content, price=price, author=author)
        # 이미지 파일명을 db에 저장, 이미지는 로컬에 저장, 이미지 경로는 config 선언
    
        db.session.add(posttable)
        db.session.commit()

        return redirect('/mainpage')
    
    return render_template('upload_product.html', title='upload', form=form)

@app.route('/product_detail/<id>', methods = ['GET', 'POST'])
def product_detail(id):
    post = Post.query.filter_by(id = id).first()
    print(post)
    return render_template('product_detail.html', title='detail', post=post)


@app.route('/edit_product/<id>', methods = ['GET', 'POST'])
def edit_product(id):
    update_product = Post.query.filter_by(id = id).first()
    form = EditForm()
   
    # print(form.keyword, form.content, form.price)
    print(form.data.get('keyword'), form.data.get('content'), form.data.get('price'))
    
    print(form.validate_on_submit())
    print(form.errors)
    if form.validate_on_submit():
    # if not form.data.get('keyword')is not "None" or not form.data.get('content') or not form.data.get('price'):
        # print("if 문 들어옴")
        update_product.keyword = form.data.get('keyword')
        update_product.content = form.data.get('content')
        update_product.price = form.data.get('price')
        db.session.commit()

        return redirect(url_for('product_detail', id = update_product.id))

    form.keyword.data = update_product.keyword
    form.content.data = update_product.content
    form.price.data = update_product.price
    # print(form.price.data)
    return render_template('edit_product.html', title='edit', post=update_product,form=form)

@app.route('/follow/<id>', methods=['GET','POST'])
def follow(id):
    userid = session['userid']
    author = User.query.filter_by(userid=userid).first()
    # user = User.query.filter_by(id=id).first()
    author.follow(id)
    db.session.commit()
    flash('You are following {}!'.format(id))
    return redirect(url_for('mypage'))



# @app.route('/unfollow/<username>', methods=['POST'])
# def unfollow(username):
#     form = EmptyForm()
#     if form.validate_on_submit():
#         user = User.query.filter_by(username=username).first()
#         if user is None:
#             flash('User {} not found.'.format(username))
#             return redirect(url_for('mainpage'))
#         if user == current_user:
#             flash('You cannot unfollow yourself!')
#             return redirect(url_for('user', username=username))
#         current_user.unfollow(user)
#         db.session.commit()
#         flash('You are not following {}.'.format(username))
#         return redirect(url_for('mypage', username=username))
#     else:
#         return redirect(url_for('mainpage'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all() # db 생성
        # print(Post.query.all())
    db.session.rollback()

    app.run(debug = True)