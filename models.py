from extensions import db

class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20),unique=False,nullable=False)
    password = db.Column(db.String(128),unique=False,nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"username : {self.username}"