from datetime import date, datetime
from src.utils.date_utils import parse_date, format_date, get_week_sunday
from flask import Blueprint, render_template, redirect, url_for, request
from src.webapp.services.auth import require_auth
from src.webapp.services.api_client import api_client

reports_bp = Blueprint('reports', __name__)


@reports_bp.route('/reports/')
@require_auth
def index():
    """Main reports page"""
    return render_template('reports/index.html')



@reports_bp.route('/reports/day/')
@require_auth
def daily_redirect():
    """Redirect to today's report"""
    today = date.today().strftime('%Y-%m-%d')
    return redirect(url_for('reports.daily', date=today))

@reports_bp.route('/reports/day/<date>', methods=['GET', 'POST'])
@require_auth
def daily(date):
    """Daily report view and save"""
    if request.method == 'POST':
        data = request.form.to_dict()
        data['date'] = date
        api_client.post('/reports/day', data)
        return redirect(url_for('reports.daily', date=date))

    report = api_client.get(f"/reports/day/{date}/get_or_create")
    return render_template('reports/day_report.html',
                         date=date,
                         report=report)

@reports_bp.route('/reports/week/')
@require_auth
def weekly_redirect():
    """Redirect to this week's report"""
    today = date.today()
    week_sunday = get_week_sunday(today)
    return redirect(url_for('reports.weekly', date=format_date(week_sunday)))


@reports_bp.route('/reports/week/<date>', methods=['GET', 'POST'])
@require_auth
def weekly(date):
    """Weekly report view and save"""
    input_date = parse_date(date)
    week_sunday = get_week_sunday(input_date)

    if request.method == 'POST':
        data = request.form.to_dict()
        data['week_sunday'] = format_date(week_sunday)
        api_client.post('/reports/week', data)
        return redirect(url_for('reports.weekly', date=date))

    report = api_client.get(f"/reports/week/{format_date(week_sunday)}/get_or_create")
    return render_template('reports/week_report.html',
                           date=date,
                           report=report)


#
#
# @reports_bp.route('/reports/month/<date>', methods=['GET', 'POST'])
# @require_auth
# def monthly(date):
#     """Monthly report view and save"""
#     if request.method == 'POST':
#         data = request.form.to_dict()
#         data['date'] = date
#         api_client.post('/reports/month', data)
#         return redirect(url_for('reports.monthly', date=date))
#
#     report = api_client.get(f"/reports/month/{date}/get_or_create")
#     return render_template('reports/monthly.html',
#                          date=date,
#                          report=report)
#
# @reports_bp.route('/reports/season/<year>/<season>', methods=['GET', 'POST'])
# @require_auth
# def seasonal(year, season):
#     """Seasonal report view and save"""
#     if request.method == 'POST':
#         data = request.form.to_dict()
#         data['year'] = year
#         data['season'] = season
#         api_client.post('/reports/season', data)
#         return redirect(url_for('reports.seasonal', year=year, season=season))
#
#     report = api_client.get(f"/reports/season/{year}/{season}")
#     return render_template('reports/seasonal.html',
#                          year=year,
#                          season=season,
#                          report=report)
#
# @reports_bp.route('/reports/year/<year>', methods=['GET', 'POST'])
# @require_auth
# def yearly(year):
#     """Yearly report view and save"""
#     if request.method == 'POST':
#         data = request.form.to_dict()
#         data['year'] = year
#         api_client.post('/reports/year', data)
#         return redirect(url_for('reports.yearly', year=year))
#
#     report = api_client.get(f"/reports/year/{year}")
#     return render_template('reports/yearly.html',
#                          year=year,
#                          report=report)