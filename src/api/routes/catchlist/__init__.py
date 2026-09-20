from flask import Blueprint
from . import catchlist

catchlist_bp = Blueprint('catchlist', __name__)

# Catch List Routes (per-user singleton resource)
catchlist_bp.add_url_rule('/api/catchlist', view_func=catchlist.get_catchlist, endpoint='get_catchlist', methods=['GET'])
catchlist_bp.add_url_rule('/api/catchlist', view_func=catchlist.update_catchlist, endpoint='update_catchlist', methods=['PUT'])