from datetime import datetime
from app import db
import json

class Analysis(db.Model):
    """Model for thread analysis results"""
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    warp_count = db.Column(db.Integer)  # Threads running lengthwise in the fabric
    weft_count = db.Column(db.Integer)  # Threads running crosswise in the fabric
    thread_density = db.Column(db.Float)  # Threads per inch/cm
    confidence_score = db.Column(db.Float)  # How confident the algorithm is in the result (0-1)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    measurement_unit = db.Column(db.String(10), default='cm')  # cm or inch
    notes = db.Column(db.Text, nullable=True)
    image_processed = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<Analysis {self.id} - {self.original_filename}>'
    
    def to_dict(self):
        """Convert analysis object to dictionary for API response"""
        return {
            'id': self.id,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'warp_count': self.warp_count,
            'weft_count': self.weft_count,
            'thread_density': self.thread_density,
            'confidence_score': self.confidence_score,
            'date_created': self.date_created.isoformat(),
            'measurement_unit': self.measurement_unit,
            'notes': self.notes,
            'image_processed': self.image_processed
        }
    
    def to_json(self):
        """Convert analysis object to JSON string"""
        return json.dumps(self.to_dict())
