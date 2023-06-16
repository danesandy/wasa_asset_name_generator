from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from name_generator import db

class User(UserMixin, db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, index=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_first_login = db.Column(db.Boolean, default=True)

    @classmethod
    def find_by_email(cls, email):
        return cls.query.filter_by(email=email).first()

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
class ServiceCode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200))

class LocationCode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200))

class ProcessCode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200))

class AssetType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200))

class Asset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_code_id = db.Column(db.Integer, db.ForeignKey('service_code.id'), nullable=False)
    location_code_id = db.Column(db.Integer, db.ForeignKey('location_code.id'), nullable=False)
    process_code_id = db.Column(db.Integer, db.ForeignKey('process_code.id'), nullable=False)
    asset_type_id = db.Column(db.Integer, db.ForeignKey('asset_type.id'), nullable=False)
    asset_number = db.Column(db.Integer, nullable=False)
    local_number = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(200), nullable=False)

    service_code = db.relationship('ServiceCode')
    location_code = db.relationship('LocationCode')
    process_code = db.relationship('ProcessCode')
    asset_type = db.relationship('AssetType')

