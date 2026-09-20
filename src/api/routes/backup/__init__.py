from flask import Blueprint
from . import backup

backup_bp = Blueprint('backup', __name__)

# Backup Routes
backup_bp.add_url_rule('/api/backup/export', view_func=backup.export_data, endpoint='export_data', methods=['GET'])
backup_bp.add_url_rule('/api/backup/import', view_func=backup.import_data, endpoint='import_data', methods=['POST'])