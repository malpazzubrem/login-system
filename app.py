import os
from flask import Flask,request,redirect,render_template
from flask_session import Session
from extensions import db, bcrypt, limiter
from routes.login import login_Bp
from models import Profile
import getpass

app = Flask(__name__)

db.init_app(app)
bcrypt.init_app(app)
limiter.init_app(app)
session = Session(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False #configuring base

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem" #configuring session
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", os.urandom(32))

app.register_blueprint(login_Bp)
@app.cli.command("create-admin")
def create_admin():
    username = input("write admin username: ")
    if Profile.query.filter_by(username=username).first():
        print("That username already exists.")
        return
    password = getpass("Password: ")
    hashed = bcrypt.generate_password_hash(password).decode('utf-8')
    user = Profile(username=username,password=hashed ,is_admin=True)

    db.session.add(user)
    db.session.commit()
    print("admin user created")

@app.cli.command("delete-admin")
def delete_admin():
    username = input("write admin username: ")
    data = Profile.query.filter_by(username=username).first()
    if data==None:
        print("no admin found")
        return
    
    print("are you sure? [y/n]")
    ans = input()

    if ans == "y":
        db.session.delete(data)
        db.session.commit()
        print("admin removed")

    else:
        print("aborted")

@app.cli.command("list-admins")
def list_admins():
    data = Profile.query.filter_by(is_admin=True)
    for i in data:
        print(i.username)


@app.route("/",methods=["GET","POST"])
def main_page():
    return render_template("mainpage.html")

@app.route("/signin",methods=["GET","POST"])
def signin():
    if request.method=="POST":
        username=request.form["username"]
        password=request.form["password"]

        hashed = bcrypt.generate_password_hash(password).decode('utf-8') #hashing passwords

        if username != '' and password != '':
            p = Profile(username=username, password=hashed) #saving in sql
            db.session.add(p)
            db.session.commit()
            user = Profile.query.filter_by(username=username).first()
            return redirect(f"/user/{user.id}")

    return render_template("sign_in.html")

@app.route("/admin",methods=["GET","POST"])
def admin_panel():
    if not session.get("is_admin"):
        return redirect("/")
    profiles = Profile.query.all()
    print("admin accesing page")

    return render_template('admin_panel.html', profiles=profiles)

@app.route("/logout")
def loging_out():
    print("admin/user loging out")
    session.clear()
    return redirect("/")

@app.route("/delete/<int:id>",methods=["GET","POST"])
def delete(id):
    if not session.get("is_admin"):
        return redirect("/")
    data = db.session.get(Profile, id)
    db.session.delete(data)
    db.session.commit()
    return redirect("/admin")

@app.route("/edit/<int:id>",methods=["POST","GET"])
def edit(id):
    if not session.get("is_admin"):
        return redirect("/")
    data = db.session.get(Profile,id)
    if request.method=="POST":
        new_username = request.form["username"]
        new_password = request.form["password"]

        if not(new_username==""):
            data.username = new_username
        if not(new_password==""):
            hashed = bcrypt.generate_password_hash(new_password).decode('utf-8')
            data.password = hashed
        
        db.session.commit()

        return redirect("/admin")

    return render_template("editing_user.html")

@app.route("/user/<int:id>")
def user_profile(id):
    user=Profile.query.filter_by(id=id).first()
    if user == None:
        print("user not found")
        return redirect("/")
    if not session.get("user_id")==user.id:
        return redirect("/")
    return render_template("user_profile.html",user=user)

if __name__ == "__main__":
    with app.app_context(): 
        db.create_all() 
    app.run(debug=True)