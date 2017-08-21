from django.conf import settings 
from jaeger_client import Config
import opentracing

try:
    # Django >= 1.10
    from django.utils.deprecation import MiddlewareMixin
except ImportError:
    # Not required for Django <= 1.9, see:
    # https://docs.djangoproject.com/en/1.10/topics/http/middleware/#upgrading-pre-django-1-10-style-middleware
    MiddlewareMixin = object

class OpenTracingMiddleware(MiddlewareMixin):
    '''
    __init__() is only called once, no arguments, when the Web server responds to the first request
    '''
    def __init__(self, get_response=None):
        self._tracer = None

    def init_tracer(self):
        return Config(config=settings.OPENTRACING_TRACER_CONFIG, service_name=settings.SERVICE_NAME).initialize_tracer()

    def process_view(self, request, view_func, view_args, view_kwargs):
        if not self._tracer._trace_all:
            print 'Tracing not enabled - leaving'
            return None

        if (self._tracer == None):
            self._tracer = init_tracer()

        if hasattr(settings, 'OPENTRACING_TRACED_ATTRIBUTES'):
            traced_attributes = getattr(settings, 'OPENTRACING_TRACED_ATTRIBUTES')
        else:
            traced_attributes = []
        self._tracer._apply_tracing(request, view_func, traced_attributes)

    def process_response(self, request, response):
        self._tracer._finish_tracing(request)
        return response

