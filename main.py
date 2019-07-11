from flask import Flask, request, redirect, render_template, session, flash
from hashutils import make_pw_hash, check_pw_hash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogs:blogs@localhost:8889/blogs'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

app.secret_key = 'y4#$(ouajsdf(87*Fil'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(120))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))


    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120))
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username=username
        self.password= make_pw_hash(password)

@app.before_request
def require_login():
    allowed_routes = ['login', 'register','index', 'blog_listings', 'home']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/newpost', methods=['POST', 'GET'])
def index():
    title_error=''
    blog_error=''
    if request.method == 'POST':
        title = request.form['b_title']
        blog = request.form['blog']
        if(not title.strip()):
            title_error="You Need a Title"
        if(not blog.strip()):
            blog_error="You need a blog"
        if(not title_error and not blog_error):
            user = User.query.filter_by(username=session['username']).first()
            new_blog = Blog(title, blog, user)
            db.session.add(new_blog)
            db.session.commit()
            #bleh = Blog.query.filter_by(title=title).all()
            #return render_template('viewblog.html',title=bleh.title, blog_body=bleh.body)
            return redirect('/blog?id='+str(new_blog.id))
        else:
            return render_template('addblog.html', title_error=title_error, blog_error=blog_error, title=title, blog=blog)
    return render_template('addblog.html')

@app.route('/blog', methods=['GET'])
def blog_listings():
    if(request.args.get('id')):
        movid = int(request.args.get('id'))
        blog = Blog.query.get(movid)
        return render_template('viewblog.html', title=blog.title, blog_body=blog.body, owner=blog.owner)
    elif(request.args.get('user')):
        userid = int(request.args.get('user'))
        blogs = Blog.query.filter_by(owner_id=userid)
        return render_template("u_blogs.html", blogs=blogs)
    else:
        blogs = Blog.query.all()
        return render_template('bloglistings.html',title="Your Blogs", blogs=blogs)

@app.route('/signup', methods=['POST', 'GET'])
def register():
    if request.method =='POST':

        user_error = ''
        pass_error = ''
        ver_error = ''

        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        if(not username or not password or not verify or ' ' in username or ' ' in password):
            flash("You can't leave anything blank and no spaces in usernames or passwords", 'error')
            return render_template('signup.html')
        if(password != verify):
            flash('Passwords must match', 'error')
            return render_template('signup.html', username=username)
        if (len(username)>20 or 3>len(username)) or (len(password)>20 or 3>len(password)):
            flash('Usernames and passwords must be between 3 and 20 characters long', 'error')
            return render_template('signup.html', username=username, password=password)
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('User already exists', 'error')
            return render_template('signup.html')
        #if not existing_user:
        else:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username']=username
            session['id']=new_user.id
            return redirect('/newpost')
    return render_template('signup.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method =='POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user and check_pw_hash(password, user.password):
            session['username']=username
            session['id']= user.id
            #print(session)
            flash('Logged In')
            return redirect('/newpost')
        elif user and not check_pw_hash(password, user.password):
            flash('User password incorrect, or user does not exist', 'error')
            return redirect('/login')
        else:
           flash('Username is incorrect or does not exist', 'error')
           return redirect('/login')
    return render_template('login.html')

@app.route('/logout', methods=['POST', 'GET'])
def log_out():
    del session['username']
    del session['id']
    return redirect('/blog')


@app.route('/', methods=['POST', 'GET'])
def home():
    authors = User.query.join(Blog).all()
    print(authors)
    return render_template('index.html', authors=authors)


if __name__ == '__main__':
    app.run()