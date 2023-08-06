from django.urls import re_path
from rest_framework_docs.views import DRFDocsView

urlpatterns = [
    # Url to view the API Docs
    re_path(r'^$', DRFDocsView.as_view(), name='drfdocs'),
]
