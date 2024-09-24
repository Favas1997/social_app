from rest_framework.throttling import SimpleRateThrottle

class SignInRateThrottle(SimpleRateThrottle):
    """
    A custom throttle class that limits the rate of sign-in attempts.
    """
    scope = 'signin'

    def get_cache_key(self, request, view):
        """
        Return the cache key for this request.
        """
        # Use IP address as the key for throttling
        return f"{self.scope}:{request.META.get('REMOTE_ADDR')}"
    
    def get_rate(self):
        """
        Define the rate limit for this throttle class.
        """
        return '5/m'  # Example: 5 requests per minute per IP address
