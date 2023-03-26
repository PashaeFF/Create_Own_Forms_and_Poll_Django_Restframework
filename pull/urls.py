from django.urls import path
from .views import Pulls, GetPull, CreateQuestionnaire

urlpatterns = [
    path('', Pulls.as_view()),
    path('create_questionnaire', CreateQuestionnaire.as_view()),
    path('create_questionnaire/<int:pk>', GetPull.as_view()),
]