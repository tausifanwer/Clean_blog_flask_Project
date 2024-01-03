from flask import Flask,render_template,request,session,redirect
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail,Message
import json
from datetime import datetime
import os,math
from werkzeug.utils import secure_filename


with open('config.json','r') as c:
    params=json.load(c)["params"]

local_server=True
app=Flask(__name__)
app.secret_key='super-secret-key'
app.config['UPLOAD_FOLDER']=params['upload_location']

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'tausifanwer81@gmail.com'
app.config['MAIL_PASSWORD'] = 'grcn fxin pkfj blwd'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail=Mail(app)

if local_server:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_url']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['production_url']
db = SQLAlchemy(app)


class Contacts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(20),unique=True, nullable=False)
    phone_num = db.Column(db.String(12), nullable=False)
    mesg = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12),nullable=True)

class Posts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    tagline = db.Column(db.String(120), nullable=False)
    slug = db.Column(db.String(21), nullable=False)
    content = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)
    img_file = db.Column(db.String(12), nullable=True)
    




@app.route("/index")
def home():
    posts = Posts.query.filter_by().all()
    last = math.ceil(len(posts)/int(params['no_of_posts']))
    page = request.args.get('page')
    if (not str(page).isnumeric()):
        page = 1
    page = int(page)
    posts = posts[(page-1)*int(params['no_of_posts']):(page-1)*int(params['no_of_posts'])+ int(params['no_of_posts'])]
    if page==1:
        prev = "#"
        next = "/index?page="+ str(page+1)
    elif page==last:
        prev = "/index?page="+ str(page-1)
        next = "#"
    else:
        prev = "/index?page="+ str(page-1)
        next = "/index?page="+ str(page+1)
    return render_template('index.html',params=params,posts=posts,prev=prev,next=next)

@app.route('/about')
def about():
    return render_template('about.html',params=params)

@app.route('/dashboard')
def dashboard():
    posts=Posts.query.all()
    return render_template('dashboard.html',params=params,posts=posts)

@app.route('/sigin', methods=['GET','POST'])
def sigin():
    # user already login
    if ('user' in session and session['user']==params['admin_user']):
        posts=Posts.query.all()
        return render_template('dashboard.html',params=params,posts=posts)

    if (request.method=='POST'):
        username=request.form.get('uname')
        userpass=request.form.get('pass')
        if (username==params['admin_user'] and  userpass==params['admin_password']):
            # session variable
            session['user']=username
            posts=Posts.query.all()

            return render_template('dashboard.html',params=params,posts=posts)
        else:
            return render_template('sigin.html',params=params)
    else:
        return render_template('sigin.html',params=params)
    
@app.route('/logout')
def logout():
    session.pop('user')
    return redirect("/index")

@app.route('/edit/<string:sno>',methods=['GET','POST'])
def edit(sno):
    if "user" in session and session['user']==params['admin_user']:
        if request.method=="POST":
            box_title = request.form.get('title')
            tline = request.form.get('tline')
            slug = request.form.get('slug')
            content = request.form.get('content')
            img_file = request.form.get('img_file')
            date = datetime.now()
            if sno != "0":
                post = Posts.query.filter_by(sno=sno).first()
                post.box_title = box_title
                post.tline = tline
                post.slug = slug
                post.content = content
                post.img_file = img_file
                post.date = date
                # db.session.add(post)
                db.session.commit()
                return redirect('/edit/'+sno)
        post=Posts.query.filter_by(sno=sno).first()
        return render_template('edit.html',params=params,post=post)

@app.route('/delete/<string:sno>',methods=['GET','POST'])
def delete(sno):
    if "user" in session and session['user']==params['admin_user']:
        post=Posts.query.filter_by(sno=sno).first()
        db.session.delete(post)
        db.session.commit()    
        return redirect('/dashboard')
    
@app.route('/postupload/<string:sno>',methods=['GET','POST'])
def postupload(sno):
    if "user" in session and session['user']==params['admin_user']:
        if request.method=="POST":
            box_title = request.form.get('title')
            tline = request.form.get('tline')
            slug = request.form.get('slug')
            content = request.form.get('content')
            img_file = request.form.get('img_file')
            date = datetime.now()
            if sno=='0':
                post = Posts(title=box_title, slug=slug, content=content, tagline=tline, img_file=img_file,date=date)
                db.session.add(post)
                db.session.commit()
        return render_template('postupload.html',params=params,sno=sno)
    


@app.route('/fileupload', methods=['GET','POST'])
def fileupload():
    if "user" in session and session['user']==params['admin_user']:
        if request.method=="POST":
            f=request.files['file1']
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))
            return "Uploaded Successfully"
        return redirect('/dashboard')


@app.route('/contact', methods=['GET','POST'])
def contact():
    if (request.method=='POST'):
        name=request.form.get('name')
        email=request.form.get('email')
        phone=request.form.get('phone')
        message=request.form.get('message')

        entry=Contacts(name=name, email=email , phone_num=phone , mesg=message,date=datetime.now() )
        db.session.add(entry)
        db.session.commit() 
        
        msg = Message('New message from blog ', sender ='tausifanwer81@gmail.com', recipients =['tausifanwer81@gmail.com'])
        msg.body = "New message from blog "+"\n"+"".join(name)+"\n"+"".join(email)+"\n"+"".join(phone)+"\n"+message
        mail.send(msg)

    return render_template('contact.html',params=params)

@app.route('/post/<string:post_slug>',methods=['GET'])
def post_route(post_slug):
    post=Posts.query.filter_by(slug=post_slug).first()
    return render_template('post.html',params=params,post=post)



app.run(debug=True)