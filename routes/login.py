from flask import Blueprint,render_template,request,session,Flask
from flask import redirect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_limiter.errors import RateLimitExceeded
from flask_bcrypt import Bcrypt

app = Flask(__name__)
login_Bp = Blueprint("login",__name__)

bcrypt = Bcrypt(app)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)
from app import Profile,db
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
db.init_app(app)

@login_Bp.route("/login",methods=["GET","POST"])
@limiter.limit("3 per minute",methods=["POST"])
def login():
    if request.method=="POST":
        username=request.form["username"]
        password=request.form["password"] #getting userdata
    
        if username != '' and password != '':
            user = Profile.query.filter_by(username=username).first() #getting base data

            if user == None:
                print("wrong username")
                return render_template("log_in.html",error="Wrong username or password" ,disabled=0)

            user_1 = bcrypt.check_password_hash(user.password, password) #checking passwords

            if user_1 and user.is_admin:
                session["user_id"] = user.id
                session["is_admin"] = user.is_admin
                print("admin login")
                return redirect('/admin')

            elif user_1:
                print('login successful')
                session["user_id"] = user.id
                return redirect(f"/user/{user.id}")
        
            else:
                print('wrong password')
                return render_template("log_in.html",error="Wrong username or password",disabled=0)

    return render_template("log_in.html")

@app.errorhandler(RateLimitExceeded)
def ratelimit_handler():
    return render_template("429.html"), 429
