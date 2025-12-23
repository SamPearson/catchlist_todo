
from flask import Blueprint
from . import tags

tags_bp = Blueprint('tags', __name__)

# Tag Routes
tags_bp.add_url_rule('/api/tags', view_func=tags.list_tags, endpoint='list_tags', methods=['GET'])
tags_bp.add_url_rule('/api/tags', view_func=tags.create_tag, endpoint='create_tag', methods=['POST'])
tags_bp.add_url_rule('/api/tags/<int:tag_id>', view_func=tags.get_tag, endpoint='get_tag', methods=['GET'])
tags_bp.add_url_rule('/api/tags/<int:tag_id>', view_func=tags.update_tag, endpoint='update_tag', methods=['PUT'])
tags_bp.add_url_rule('/api/tags/<int:tag_id>', view_func=tags.delete_tag, endpoint='delete_tag', methods=['DELETE'])
tags_bp.add_url_rule("/api/tags/attach", view_func=tags.attach_tag, methods=["POST"])
tags_bp.add_url_rule("/api/tags/detach", view_func=tags.detach_tag, methods=["POST"])