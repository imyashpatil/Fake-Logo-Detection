from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

    # Define the reverse relationship to ClassificationResult
    classification_results = db.relationship('ClassificationResult', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.email}>'


class ClassificationResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    original_image = db.Column(db.String(255), nullable=False)      # uploaded image filename
    processed_image = db.Column(db.String(255), nullable=True)      # processed image filename
    confidence_score = db.Column(db.Float, nullable=False)          # model confidence
    logo_status = db.Column(db.String(20), nullable=False)          # "real" or "fake"

    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<ClassificationResult {self.logo_status}, {self.confidence_score}>'
