from oauth2_provider.views.mixins import ProtectedResourceMixin, OAuthLibMixin
from .base import method_decorator, csrf_exempt, view_catch_error, BaseCrudView, BaseView
from .lookups import ChoicesView


def set_user(f):
    def wrap(self, request, *args, **kwargs):
        self.user = request.resource_owner
        return f(self, request=request, *args, **kwargs)

    wrap.__doc__ = f.__doc__
    wrap.__name__ = f.__name__
    return wrap


@method_decorator([csrf_exempt, view_catch_error, set_user], name='dispatch')
class OauthChoiceView(ProtectedResourceMixin, OAuthLibMixin, ChoicesView):
    pass


@method_decorator([csrf_exempt, view_catch_error, set_user], name='dispatch')
class OauthCrudView(ProtectedResourceMixin, OAuthLibMixin, BaseCrudView):
    def __init__(self, *args, **kwargs):
        super(OauthCrudView, self).__init__(*args, **kwargs)
        self.user = None


@method_decorator([csrf_exempt, view_catch_error, set_user], name='dispatch')
class OauthFunctionalView(ProtectedResourceMixin, OAuthLibMixin, BaseView):
    pass
