from rest_framework.routers import DefaultRouter
from django.urls import path, include
from core.views import ProfileViewSet, ProfileExportView, GitHubLoginView, GitHubCallbackView, github_login_init , LogoutView,TokenRefreshView
#from rest_framework_simplejwt.views import TokenRefreshView

router = DefaultRouter()
router.register(r'profiles', ProfileViewSet, basename='profile')

# urlpatterns = [
#     path('', include(router.urls)),
#     ]

urlpatterns = [
    # OAuth flow
    path('auth/github', GitHubLoginView.as_view(), name='github-login'),
    #path('auth/github', github_login_init, name='github-login'),
    path('auth/github/callback', GitHubCallbackView.as_view(), name='github-callback'),
    
    # Token Management (Must be POST)
    path('auth/refresh', TokenRefreshView.as_view(), name='token-refresh'),
    path('auth/logout', LogoutView.as_view(), name='logout'),
    path('profiles/export', ProfileExportView.as_view(), name='profile-export'),
    path('api/', include(router.urls)), 
] #+ router.urls