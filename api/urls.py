from rest_framework.urls import url

from api.views import FilUploadView


urlpatterns = [
    url('', FilUploadView.as_view()),
]
