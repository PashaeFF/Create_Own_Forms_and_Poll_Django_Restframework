from django.urls import path
from .views import Polls, GetPoll, CreateQuestionnaire

urlpatterns = [
    path('', Polls.as_view()),
    path('create_questionnaire', CreateQuestionnaire.as_view()),
    path('create_questionnaire/<int:pk>', GetPoll.as_view()),
]