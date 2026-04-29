from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework import viewsets,permissions
from .permissions import IsAdminOrReadOnly # Custom RBAC class [cite: 134
from rest_framework.response import Response
from rest_framework.mixins import ListModelMixin
from rest_framework.decorators import action
from rest_framework import status
from .models import Profile
from .serializer import ProfileSerializer
from .filters import ProfileFilter, CustomOrderingFilter
from .pagination import ProfilePagination
import csv
from django.http import HttpResponse
from datetime import datetime
from rest_framework.views import APIView
from django.shortcuts import redirect
from django.conf import settings
import requests
from rest_framework_simplejwt.tokens import RefreshToken
from core.models import User
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated


# Create your views here.


class ProfileViewSet(ListModelMixin, viewsets.GenericViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    filter_backends = [DjangoFilterBackend, CustomOrderingFilter, SearchFilter]
    filterset_class = ProfileFilter
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    ordering_fields = ['age', 'gender_probability', 'country_probability']
    pagination_class = ProfilePagination

    def list(self, request, *args, **kwargs):
        # 1. Apply the filters first
        queryset = self.filter_queryset(self.get_queryset())

        # 2. Apply pagination to the filtered queryset
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        # 3. Fallback for no pagination
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='search')
    def search_profiles(self, request):
        # 1. Get the base queryset
        queryset = self.get_queryset()
        
        # 2. Manually trigger the ProfileFilter
        filterset = self.filterset_class(request.GET, queryset=queryset, request=request)
        
        if filterset.is_valid():
            queryset = filterset.qs
        
        # 3. Use your custom pagination to ensure the "Envelope" is correct
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        # Fallback for non-paginated (though CustomPagination should handle this)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
# Create your views here.
# views_profiles.py


class ProfileExportView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        response = HttpResponse(content_type='text/csv') # [cite: 206]
        response['Content-Disposition'] = f'attachment; filename="profiles_{timestamp}.csv"' # [cite: 208]

        writer = csv.writer(response)
        # Required Column Order [cite: 209, 210]
        writer.writerow(['id', 'name', 'gender', 'gender_probability', 'age', 
                         'age_group', 'country_id', 'country_name', 
                         'country_probability', 'created_at'])

        profiles = ProfileFilter(request.GET, queryset=Profile.objects.all()).qs
        for p in profiles:
            writer.writerow([p.id, p.name, p.gender, p.gender_probability, p.age, 
                             p.age_group, p.country_id, p.country_name, 
                             p.country_probability, p.created_at])
        return response



class GitHubCallbackView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        code = request.GET.get('code')
        state = request.GET.get('state')
        # Retrieve state from session to prevent CSRF
        saved_state = request.session.get('oauth_state')

        # 1. VALIDATION (Required for Grade)
        if not code:
            return Response({"status": "error", "message": "Missing code"}, status=400)
        if not state or state != saved_state:
            return Response({"status": "error", "message": "Invalid state"}, status=400)

        # 2. EXCHANGE CODE FOR GITHUB TOKEN
        token_url = "https://github.com/login/oauth/access_token"
        payload = {
            'client_id': settings.GITHUB_CLIENT_ID,
            'client_secret': settings.GITHUB_CLIENT_SECRET,
            'code': code,
        }
        headers = {'Accept': 'application/json'}
        
        res = requests.post(token_url, data=payload, headers=headers)
        gh_data = res.json()
        
        if "access_token" not in gh_data:
            return Response({"status": "error", "message": "GitHub auth failed"}, status=400)

        # 3. FETCH USER PROFILE FROM GITHUB
        user_res = requests.get(
            "https://api.github.com/user",
            headers={'Authorization': f"token {gh_data['access_token']}"}
        )
        gh_user = user_res.json()

        # 4. CREATE OR UPDATE LOCAL USER
        # Maps GitHub ID to our UUID-based User model
        user, created = User.objects.update_or_create(
            github_id=gh_user['id'],
            defaults={
                'username': gh_user['login'],
                'email': gh_user.get('email'),
                'avatar_url': gh_user.get('avatar_url'),
            }
        )

        # 5. ISSUE JWT TOKENS (Rotating pair)
        refresh = RefreshToken.for_user(user)
        
        return Response({
            "status": "success",
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
            "user": {
                "id": str(user.id),
                "username": user.username,
                "role": user.role
            }
        })
    


class ProfileExportView(APIView):
    # Requirement: Only authenticated users can export data
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # 1. Apply the same filtering logic as the list view
        queryset = Profile.objects.all()
        filterset = ProfileFilter(request.GET, queryset=queryset, request=request)
        
        if not filterset.is_valid():
            return HttpResponse("Invalid query parameters", status=400)
            
        profiles = filterset.qs

        # 2. Setup CSV response with timestamped filename
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="profiles_{timestamp}.csv"'

        writer = csv.writer(response)
        
        # 3. Mandatory Column Order
        writer.writerow([
            'id', 'name', 'gender', 'gender_probability', 'age', 
            'age_group', 'country_id', 'country_name', 
            'country_probability', 'created_at'
        ])

        # 4. Write data rows
        for p in profiles:
            writer.writerow([
                p.id, 
                p.name, 
                p.gender, 
                p.gender_probability, 
                p.age, 
                p.age_group, 
                p.country_id, 
                p.country_name, 
                p.country_probability, 
                p.created_at.strftime("%Y-%m-%d %H:%M:%S")
            ])

        return response