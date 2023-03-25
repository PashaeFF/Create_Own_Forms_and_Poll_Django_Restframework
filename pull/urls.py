from django.urls import path
from .views import Pull, CreateQuestionnaire

urlpatterns = [
    path('', Pull.as_view()),
    path('create_questionnaire', CreateQuestionnaire.as_view()),
]