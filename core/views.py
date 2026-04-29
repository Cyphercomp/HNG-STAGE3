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
from rest_framework import permissions
from django.shortcuts import redirect
from django.conf import settings
import requests
from rest_framework_simplejwt.tokens import RefreshToken


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


# class WebGitHubCallback(APIView):
#     def get(self, request):
#         # 1. Exchange code for GitHub tokens
#         # 2. Authenticate/Create user
#         user = perform_github_auth(request.GET.get('code'))

#         # 3. Generate JWT tokens
#         refresh = RefreshToken.for_user(user)
#         access_token = str(refresh.access_token)
#         refresh_token = str(refresh)

#         # 4. Set HTTP-only cookies
#         response = redirect('dashboard')
#         response.set_cookie(
#             key='access_token',
#             value=access_token,
#             httponly=True, # Prevents JS access 
#             secure=True,   # Only over HTTPS [cite: 258]
#             samesite='Lax',
#             max_age=180    # 3 minutes [cite: 113]
#         )
#         response.set_cookie(
#             key='refresh_token',
#             value=refresh_token,
#             httponly=True,
#             secure=True,
#             samesite='Lax',
#             max_age=300    # 5 minutes [cite: 115]
#         )
#         return response