from django.urls import path
from .views import FormsAll, CreateForm, ViewForm, GetListForms, GetFilledForm, DeleteFilledForm, FillForm

urlpatterns = [
    path('', FormsAll.as_view()),
    path('form/', CreateForm.as_view()),
    path('<int:pk>', ViewForm.as_view()),
    path('<int:pk>/fillform/', FillForm.as_view()),
    path('<int:pk>/list/', GetListForms.as_view()),
    path('delete_filled_form/<int:wk>', DeleteFilledForm.as_view()),
    path('<int:pk>/filled_form/<int:wk>/view', GetFilledForm.as_view()),
    # path('<int:pk>/filled_form/<int:wk>/download', FormsView.filled_form_to_xlsx),
    
]