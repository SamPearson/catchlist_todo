from flask import Blueprint
from . import timeframes

timeframes_bp = Blueprint("timeframes", __name__)

timeframes_bp.add_url_rule(
    "/api/timeframes/kinds",
    view_func=timeframes.list_timeframe_kinds,
    endpoint="list_timeframe_kinds",
    methods=["GET"],
)

timeframes_bp.add_url_rule(
    "/api/timeframes",
    view_func=timeframes.list_timeframes,
    endpoint="list_timeframes",
    methods=["GET"],
)

timeframes_bp.add_url_rule(
    "/api/timeframes",
    view_func=timeframes.create_timeframe,
    endpoint="create_timeframe",
    methods=["POST"],
)

timeframes_bp.add_url_rule(
    "/api/timeframes/<int:timeframe_id>",
    view_func=timeframes.get_timeframe_by_id,
    endpoint="get_timeframe_by_id",
    methods=["GET"],
)


timeframes_bp.add_url_rule(
    "/api/timeframes/<string:kind>",
    view_func=timeframes.get_timeframe_today,
    endpoint="get_timeframe_today",
    methods=["GET"],
)


timeframes_bp.add_url_rule(
    "/api/timeframes/<string:kind>/<string:date>",
    view_func=timeframes.get_timeframe,
    endpoint="get_timeframe",
    methods=["GET"],
)

