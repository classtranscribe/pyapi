from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class Shipment(db.Model):
    """
    Shipment Model
    """
    id = db.Column(db.Integer, primary_key=True)
    destination = db.Column(db.String(80))
    source = db.Column(db.String(120))
    current_location = db.Column(db.String(120))
    status = db.Column(db.String(120))
    item = db.Column(db.String(120))
    description = db.Column(db.String(120))
    tracking_number = db.Column(db.String(120), nullable=True)
    arrival = db.Column(db.String(120))
    def __repr__(self):
        return '<Shipment %r>' % self.item

    def __init__(self, description, source, current_location, status, item, tracking_number, arrival, destination):

        self.description =  description
        self.destination =  destination
        self.source = source
        self.current_location = current_location
        self.status = status
        self.item = item
        self.tracking_number = tracking_number
        self.arrival = arrival

