from oauth2_provider.views.mixins import ProtectedResourceMixin, OAuthLibMixin
from .base import method_decorator, csrf_exempt, view_catch_error, BaseCrudView, BaseView
from .lookups import ChoicesView


@method_decorator([csrf_exempt, view_catch_error], name='dispatch')
class OauthChoiceView(ProtectedResourceMixin, OAuthLibMixin, ChoicesView):
    pass


@method_decorator([csrf_exempt, view_catch_error], name='dispatch')
class OauthCrudView(ProtectedResourceMixin, OAuthLibMixin, BaseCrudView):
    pass


@method_decorator([csrf_exempt, view_catch_error], name='dispatch')
class OauthFunctionalView(ProtectedResourceMixin, OAuthLibMixin, BaseView):
    pass
