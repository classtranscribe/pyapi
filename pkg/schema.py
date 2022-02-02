from flask_marshmallow import Marshmallow
ma = Marshmallow()
class ShipmentSchema(ma.Schema):
    """
    Schema
    """
    class Meta:
        fields = (
        'id',
        'item',
        'description',
        'status',
        'tracking_number',
        'current_location',
        'source',
        'destination',
        'description',
        'arrival'
        )