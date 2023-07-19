import datetime
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib import messages
import logging

logger = logging.getLogger(__name__)


class SessionTimeoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            last_activity = request.session.get("last_activity", None)
            if last_activity:
                last_activity = datetime.datetime.strptime(
                    last_activity, "%Y-%m-%d %H:%M:%S"
                )
                time_difference = datetime.datetime.now() - last_activity
                if time_difference.seconds > 180:
                    die_time = last_activity + datetime.timedelta(minutes=3)
                    logger.info(
                        f"forced_logout_action: User {request.user.username} logged out, dead since {die_time}."
                    )
                    logout(request)
                    messages.error(
                        request,
                        "Your session was terminated due to inactivity. Please login again.",
                    )
                    return redirect("login")
            request.session["last_activity"] = current_time
        response = self.get_response(request)
        return response
