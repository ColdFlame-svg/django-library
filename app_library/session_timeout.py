from django.contrib.auth import logout
from django.shortcuts import redirect
from django.utils import timezone
from datetime import timedelta

class SessionTimeoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            last_activity = request.session.get('last_activity')
            if last_activity:
                # Convert the stored last_activity string back to datetime
                last_activity = timezone.datetime.fromisoformat(last_activity)

                time_difference = timezone.now() - last_activity
                if time_difference > timedelta(minutes=30):  # Set your timeout here
                    logout(request)
                    return redirect('login')  # Redirect to login page after timeout
            request.session['last_activity'] = timezone.now().isoformat()  # Store as ISO format string

        response = self.get_response(request)
        return response
