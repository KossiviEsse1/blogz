from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:build-a-blog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(120))

    def __init__(self, title, body):
        self.title = title
        self.body = body


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
            new_blog = Blog(title, blog)
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
        return render_template('viewblog.html', title=blog.title, blog_body=blog.body)
    else:
        blogs = Blog.query.all()
        return render_template('bloglistings.html',title="Your Blogs", blogs=blogs)

#@app.route('')


if __name__ == '__main__':
    app.run()