from flask import Blueprint
from . import projects

projects_bp = Blueprint("projects", __name__)

# Project Routes
projects_bp.add_url_rule("/api/projects", view_func=projects.list_projects, methods=["GET"])
projects_bp.add_url_rule("/api/projects", view_func=projects.create_project, methods=["POST"])
projects_bp.add_url_rule("/api/projects/<int:project_id>", view_func=projects.get_project, methods=["GET"])
projects_bp.add_url_rule("/api/projects/<int:project_id>", view_func=projects.update_project, methods=["PUT"])
projects_bp.add_url_rule("/api/projects/<int:project_id>", view_func=projects.delete_project, methods=["DELETE"])

# Project State Management Routes
projects_bp.add_url_rule("/api/projects/<int:project_id>/complete", view_func=projects.complete_project, methods=["PATCH"])
projects_bp.add_url_rule("/api/projects/<int:project_id>/uncomplete", view_func=projects.uncomplete_project, methods=["PATCH"])
projects_bp.add_url_rule("/api/projects/<int:project_id>/activate", view_func=projects.activate_project, methods=["PATCH"])
projects_bp.add_url_rule("/api/projects/<int:project_id>/deactivate", view_func=projects.deactivate_project, methods=["PATCH"])
projects_bp.add_url_rule("/api/projects/<int:project_id>/status", view_func=projects.change_project_status, methods=["PATCH"])

# Project Task Routes
projects_bp.add_url_rule("/api/projects/<int:project_id>/tasks", view_func=projects.get_project_tasks, methods=["GET"])
projects_bp.add_url_rule("/api/projects/<int:project_id>/tasks", view_func=projects.create_project_task, methods=["POST"])
