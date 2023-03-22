from rest_framework import status
from auth2.models import User
from .models import Form, FilledForms
from rest_framework.response import Response
from rest_framework.decorators import APIView
from .utils.check_auth import authorization
from .utils.helper import check_values_for_add_form, fill_form, filled_form_to_xlsx
from .serializers import FilledFormsSerializer, FormSerializer, CreateValuesSerializer, FillFormSerializer
from auth2.serializers import UserSerializer
import os, shutil
from drf_yasg.utils import swagger_auto_schema


class FormsAll(APIView):
    @swagger_auto_schema(operation_id="Forms All", tags=['Forms All'])
    def get(self, request):
        if authorization(request):
            user = User.objects.filter(id=authorization(request)['id']).first()
            forms = Form.objects.all()
            serializer = UserSerializer(user)
            context = {
                'title':'Create your own form',
                'forms': forms.values(),
                'user':serializer.data
            }

            return Response({"context":context}, status=status.HTTP_200_OK)
 

class CreateForm(APIView):
    @swagger_auto_schema(operation_id="Create Form", request_body=FormSerializer, tags=['Create New Form'])
    def post(self, request):
        if authorization(request):
            user = User.objects.filter(id=authorization(request)['id']).first()
            if user.company == True:
                form = request.data
                check_url = Form.objects.filter(url=form['url']).first()
                if check_url:
                    return Response({'error':'Url is available'}, status=status.HTTP_409_CONFLICT)
                else:
                    new_form = Form.objects.create(owner_id_id=user.id, url=form['url'], form_name=form['form_name'])
                    new_form.save()
                    return Response({'created':{
                                    'Email':user.email,
                                    'Url':form['url'],
                                    'Fullname':user.fullname,
                                    'Form name':form['form_name']
                                }}, status=status.HTTP_201_CREATED)
            else:
                return Response({"error":"You don't have permission"})


class ViewForm(APIView):
    @swagger_auto_schema(operation_id="View Form", tags=['Created Form'])
    def get(self, request, pk=None):
        if authorization(request):
            form_pk = Form.objects.filter(id=pk).first()
            images_path = f'/static/media/{pk}/'
            if form_pk:
                if authorization(request)['id'] == form_pk.owner_id_id:
                    values = form_pk.values
                    if len(values) < 1:
                        message = 'The form is empty, fill in your information'
                        return Response({'error':message}, status=status.HTTP_200_OK)
                    context = {
                        'title':form_pk.form_name,
                        'id':form_pk.id,
                        'owner':form_pk.owner_id_id,
                        'url':form_pk.url,
                        'images_path':images_path,
                        'data':values
                    }
                    return Response(context, status=status.HTTP_200_OK)
                else:
                    return Response({'message':'Not access'})
            else:
                message = 'Form not found'
                return Response({'error':message}, status=status.HTTP_200_OK)

    ####### CREATE FORM VALUES ######
    @swagger_auto_schema(operation_id="Create Form Values", tags=['Created Form'],
                         operation_description="""{
                            "question_field_1": {
                                        "question_field_1_1_title":"First Title",
                                        "question_field_1_1_description":"Description 1",
                                        "question_field_1_1_image":"https://images.pexels.com/photos/268533/pexels-photo-268533.jpeg?cs=srgb&dl=pexels-pixabay-268533.jpg&fm=jpg",
                                        "question_field_1_1_uploaded_image":"file field",
                                        "question_field_1_1_youtube":"youtube url",
                                        "question_field_1_1_url":"url",
                                        "question_field_1_1_button":"button 1",
                                        "question_field_1_2_button":"button 2",
                                        "question_field_1_1_input":"",
                                        "question_field_1_1_values":"",
                                        "question_field_1_1_required":"on",
                                        "question_field_1_1_allow":"on",
                                        "question_field_1_1_one_selection":"on"
                                        }
                                    }""",
                            request_body=CreateValuesSerializer)
    
    def post(self, request, pk=None):
        if authorization(request):
            form_pk = Form.objects.filter(id=pk).first()
            files_path = f'/static/'
            if form_pk:
                if authorization(request)['id'] == form_pk.owner_id_id:
                    if 'message' in check_values_for_add_form(request, pk, form_pk).keys():
                        return Response(check_values_for_add_form(request, pk, form_pk)['message'], status=status.HTTP_405_METHOD_NOT_ALLOWED)
                    else:
                        Form.objects.filter(id=pk).update(values=check_values_for_add_form(request, pk, form_pk))
                    return Response({'success':'Form created'}, status=status.HTTP_201_CREATED)
                else:
                    return Response({'message':'Not access'})
            else:
                return Response({'error':'Form not found'}, status=status.HTTP_404_NOT_FOUND)


    @swagger_auto_schema(operation_id="Delete Form", tags=['Created Form'])
    def delete(self, request, pk=None):
        if authorization(request):
            form_pk = Form.objects.filter(id=pk).first()
            if form_pk:
                if authorization(request)['id'] == form_pk.owner_id_id:
                    if " " in form_pk.form_name:
                        file_name = f'{form_pk.form_name.replace(" ","_")}.xlsx'
                    else:
                        file_name = f'{form_pk.form_name}.xlsx'
                    images_path = f'static/media/{pk}/'
                    xlsx_path = 'static/xlsx_files/form/'
                    if form_pk:
                        Form.objects.filter(id=pk).delete()
                        shutil.rmtree(images_path, ignore_errors=True)
                        try:
                            os.remove(xlsx_path+file_name)
                        except:
                            pass
                        message = f'The form with the {form_pk.url} has been deleted'
                        return Response({'success':message}, status=status.HTTP_200_OK)
                else:
                    return Response({'message':'not access'})
            else:
                message = 'Form not found'
                return Response({'error':message}, status=status.HTTP_404_NOT_FOUND)


class GetListForms(APIView):
    @swagger_auto_schema(operation_description="", operation_id="List filled forms", tags=['Filled forms'])
    def get(self, request, pk):
        if authorization(request):
            form_pk = FilledForms.objects.filter(form_id_id=pk).all()
            get_form = Form.objects.filter(id=pk).first()
            if get_form:
                if form_pk:
                    if authorization(request)['id'] == get_form.owner_id_id:
                        context = {
                            'title':get_form.form_name,
                            'id':get_form.id,
                            'owner_id':get_form.owner_id_id,
                            'url':get_form.url,
                        }
                        serializer_class = FilledFormsSerializer(form_pk, many=True)
                        return Response({"context":context, "data":serializer_class.data})
                    else:
                        return Response({'message':'Not access'})
                else:
                    message = f'No form has been filled for the "{get_form.form_name}"'
                    return Response({'error':message}, status=status.HTTP_200_OK)
            else:
                message = 'Form not found'
                return Response({'error':message}, status=status.HTTP_200_OK)


class FillForm(APIView):
    @swagger_auto_schema(operation_id="Fill Form Get", tags=['Form'])
    def get(self, request, pk=None):
        if authorization(request):
            form_pk = Form.objects.filter(id=pk).first()
            images_path = f'/static/media/{pk}/'
            if form_pk:
                values = form_pk.values
                if len(values) < 1:
                    message = 'The form is empty, fill in your information'
                    return Response({'error':message}, status=status.HTTP_204_NO_CONTENT)
                context = {
                    'title':form_pk.form_name,
                    'id':form_pk.id,
                    'url':form_pk.url,
                    'images_path':images_path,
                    'data':values
                }
                return Response(context, status=status.HTTP_200_OK)
            else:
                message = 'Form not found'
                return Response({'error':message}, status=status.HTTP_204_NO_CONTENT)


    @swagger_auto_schema(operation_id="Fill Form post", tags=['Form'], request_body=FillFormSerializer)
    def post(self, request, pk=None):
        if authorization(request):
            form_pk = Form.objects.filter(id=pk).first()
            user = User.objects.filter(id=authorization(request)['id']).first()
            #### filled form post request
            FilledForms.objects.create(person_id=user, filled_form=fill_form(request, pk, form_pk), form_id_id=form_pk.id)
            Form.objects.filter(id=form_pk.id).update(forms_count=form_pk.forms_count+1)
            message = 'Form filled successfull'
            return Response({'success':message}, status=status.HTTP_201_CREATED)


class GetFilledForm(APIView):
    @swagger_auto_schema(operation_id="Filled Form", tags=['Filled forms'])
    def get(self, request, pk=None, wk=None):
        if authorization(request):
            images_path = f'/static/media/{pk}/'
            form_pk = Form.objects.filter(id=pk).first()
            if form_pk:
                if authorization(request)['id'] == form_pk.owner_id_id:
                    filled = FilledForms.objects.filter(id=wk).first()
                    if filled:
                        filled_form_to_xlsx(request, pk, wk)
                        context = {
                            "title":form_pk.form_name,
                            "id":form_pk.id,
                            "url":form_pk.url,
                            "images_path":images_path,
                            "download_xlsx_file":filled_form_to_xlsx(request, pk, wk)
                            }
                        form = {}
                        for key, value in form_pk.values.items():
                            for key_filled, value_filled in filled.filled_form.items():
                                if key == key_filled:
                                    value.update({"answer":value_filled})
                                form.update({key:value})
                        if len(filled.filled_form) < 1:
                            message = 'Form is empty'
                            return Response({'error':message}, status=status.HTTP_404_NOT_FOUND)
                        return Response({"context":context, "form":form} , status=status.HTTP_200_OK)
                    message = 'Form not found'
                    return Response({'error':message}, status=status.HTTP_404_NOT_FOUND)
                else:
                    return Response({'message':'Not access'})
            else:
                message = 'Form not found'
                return Response({'error':message}, status=status.HTTP_404_NOT_FOUND)
    

class DeleteFilledForm(APIView):
    @swagger_auto_schema(operation_id="Delete Filled Form", tags=['Filled forms'])
    def delete(self, request, wk):
        if authorization(request):
            form_pk = FilledForms.objects.filter(id=wk).first()
            if form_pk:
                check_owner = Form.objects.filter(id=form_pk.form_id_id).first()
                if authorization(request)['id'] == check_owner.owner_id_id:
                    user = User.objects.filter(id=form_pk.person_id_id).first()
                    if " " in user.fullname:
                        file_name = f'{user.fullname.replace(" ","_")}.xlsx'
                    else:
                        file_name = f'{user.fullname}.xlsx'
                    forms_count = Form.objects.filter(id=form_pk.form_id_id).first()
                    name = user.fullname
                    xlsx_path = f'static/xlsx_files/filled_form/{forms_count.id}/'
                    delete_this_form = FilledForms.objects.filter(id=wk)
                    delete_this_form.delete()
                    Form.objects.filter(id=form_pk.form_id_id).update(forms_count=forms_count.forms_count-1)
                    try:
                        os.remove(xlsx_path+file_name)
                    except:
                        pass
                    message = f'The form filled by {name} has been deleted'
                    return Response({'success':message}, status=status.HTTP_202_ACCEPTED)
                else:
                    return Response({'message':'Not access'})
            else:
                message = 'Form not found'
                return Response({'error':message}, status=status.HTTP_404_NOT_FOUND)  
            