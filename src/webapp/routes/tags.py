from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from src.webapp.services.auth import require_auth
from src.webapp.services.api_client import api_client

tags_bp = Blueprint('tags', __name__)


@tags_bp.route('/tags', methods=['GET'])
@require_auth
def tags():
    # Fetch list of tags from the API
    tags_data = api_client.get('/tags')

    # pass the tag list to the html template
    return render_template('tags.html', tags=tags_data)


@tags_bp.route('/tags', methods=['POST'])
@require_auth
def create_tag():
    """Handle tag creation via form submission"""
    data = {
        'name': request.form.get('name'),
        'color': request.form.get('color', '#6c757d')
    }
    api_client.post('/tags', data)
    return redirect(url_for('tags.tags'))



@tags_bp.route('/tags/<tag_id>', methods=['POST'])
@require_auth
def delete_tag(tag_id):
    """Handle tag deletion via form submission"""
    if request.form.get('_method') == 'DELETE':
        api_client.delete(f'/tags/{tag_id}')
        return redirect(url_for('tags.tags'))
    return '', 405  # Method not allowed if not a DELETE



@tags_bp.route('/tags/<tag_id>/edit', methods=['POST'])
@require_auth
def edit_tag(tag_id):
    """Handle tag updates via form submission"""
    data = {
        'name': request.form.get('name'),
        'color': request.form.get('color')
    }
    api_client.put(f'/tags/{tag_id}', data)
    return redirect(url_for('tags.tags'))
