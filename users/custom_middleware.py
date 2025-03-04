from django.contrib.auth import logout

class EnsureUserActivationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # Reload user from database to check if their status changed
            request.user.refresh_from_db()

            # If the user is still inactive, force logout
            if not request.user.is_active:
                logout(request)

        response = self.get_response(request)
        return response