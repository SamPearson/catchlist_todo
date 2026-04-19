from flask import render_template
from . import demo_bp


@demo_bp.route('/')
def index():
    """Component demonstration page for UI testing"""
    return render_template('pages/component_demo/component_demo.html')


@demo_bp.route('/tasks/')
def tasks():
    """Component demonstration page for UI testing"""
    return render_template('pages/component_demo/task_component_demo.html')