class UserActivityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Track user activity if user is authenticated
        if request.user.is_authenticated:
           # request.user.last_activity = timezone.now()
            request.user.save(update_fields=['last_activity'])
        
        return response