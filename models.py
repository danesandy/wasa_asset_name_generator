from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

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

    service_code = db.relationship('ServiceCode')
    location_code = db.relationship('LocationCode')
    process_code = db.relationship('ProcessCode')
    asset_type = db.relationship('AssetType')

