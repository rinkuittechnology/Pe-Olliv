from django.urls import path
from .views import (
    RegisterView,
    LoginView,
    ProfileView,
    ProfileListCreateView,
    ProfileRetrieveUpdateDestroyView,
    IFSCLookupView,
    ImageUploadView,
    ImageListView,
    ImageDownloadView,
    SetAuthCookieView,
    ClearAuthCookiesView,
    CheckAuthCookiesView,
    FileUploadView,
    UserFilesListView,
    FileDownloadView,
    DummyDataTableView  

)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profiles/', ProfileListCreateView.as_view(), name='profile-list'),
    path('profiles/<int:pk>/', ProfileRetrieveUpdateDestroyView.as_view(), name='profile-detail'),

    path('ifsc/<str:ifsc_code>/', IFSCLookupView.as_view(), name='ifsc-lookup'),

    path('images/upload/', ImageUploadView.as_view(), name='image-upload'),
    path('images/', ImageListView.as_view(), name='image-list'),
    path('images/<int:pk>/download/', ImageDownloadView.as_view(), name='image-download'),


    path('auth/cookies/set/', SetAuthCookieView.as_view(), name='set-auth-cookies'),
    path('auth/cookies/clear/', ClearAuthCookiesView.as_view(), name='clear-auth-cookies'),
    path('auth/cookies/check/', CheckAuthCookiesView.as_view(), name='check-auth-cookies'),

    path('files/upload/', FileUploadView.as_view(), name='file-upload'),
    path('files/', UserFilesListView.as_view(), name='user-files-list'),
    path('files/<int:pk>/download/', FileDownloadView.as_view(), name='file-download'),

    path('dummy-data/', DummyDataTableView.as_view(), name='dummy-data-table'),
    
    ]