from flask import Blueprint
from . import projects

projects_bp = Blueprint("projects", __name__)

# Project Routes
projects_bp.add_url_rule("/api/projects", view_func=projects.list_projects, methods=["GET"])
projects_bp.add_url_rule("/api/projects", view_func=projects.create_project, methods=["POST"])
projects_bp.add_url_rule("/api/projects/<int:project_id>", view_func=projects.get_project, methods=["GET"])
projects_bp.add_url_rule("/api/projects/<int:project_id>", view_func=projects.update_project, methods=["PUT"])
projects_bp.add_url_rule("/api/projects/<int:project_id>", view_func=projects.delete_project, methods=["DELETE"])

# Project Task Routes
projects_bp.add_url_rule("/api/projects/<int:project_id>/tasks", view_func=projects.get_project_tasks, methods=["GET"])
projects_bp.add_url_rule("/api/projects/<int:project_id>/tasks", view_func=projects.create_project_task, methods=["POST"])
projects_bp.add_url_rule("/api/projects/<int:project_id>/tasks/<int:task_id>", view_func=projects.update_project_task, methods=["PUT"])
projects_bp.add_url_rule("/api/projects/<int:project_id>/tasks/<int:task_id>", view_func=projects.delete_project_task, methods=["DELETE"])