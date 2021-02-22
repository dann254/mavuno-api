from django.utils.cache import add_never_cache_headers

class DisableClientSideCachingMiddleware(object):
    """
    Browsers tend to cache REST API calls, unless some specific HTTP headers are added by our
    application.

    - no_cache
    - no_store
    - must_revalidate
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_response(self, request, response):
        add_never_cache_headers(response)
        return response
