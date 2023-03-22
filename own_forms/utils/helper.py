from rest_framework import status
from ..models import Form, FilledForms
from auth2.models import User
from rest_framework.response import Response
from .image_check_and_upload import check_image_upload_errors, image_upload
from ..utils.check_auth import authorization
import xlsxwriter, os


def check_values_for_add_form(request, pk, form_pk):
    form_keys = ['checkbox_field', 'question_field']
    ### Dict to add to the database
    my_dict = {}
    form = request.data
    count = 0
    if len(form) < 1:
        message = 'Form is empty'
        return {'message':{'error':message}}
    for f_key, add in form.items():
        f_key_parts = f_key.split("_")
        for nums, (key, add_item )in enumerate(add.items(), 1):
            key_parts = key.split("_")
            #### Index 0 of the dict is set to 'title'. A title must be included. Returns an error if 'header' is missing or has been modified
            if nums == 1:
                if key_parts[-1] != 'title':
                    message = 'Title has not been added'
                    return {'message':{'error':message}}
            # #### We compare this (field_name) to a list of 'form_keys' so that other keys in the frontend are not located in the database
            field_name = "_".join(key_parts[:3])
            field_check_name = "_".join(f_key_parts[:2])
            if key_parts[-1] == 'description':
                if len(add_item) == 0:
                    continue
            if len(add_item) < 1:
                message = 'Inputs cannot be empty'
                return {'message':{'error':message}}
            if field_check_name not in form_keys:
                message = 'Something went wrong'
                return {'message':{'error':message}}
            if f_key not in my_dict:
                my_dict[f_key] = {'title':None,'description':None,'image':[],'uploaded_image':[],'youtube':[],
                                        'url':[],'button':[],'input':None,'values':[], 'required':None, 'allow':None, 'one_selection':None, 'counter':0}               
            ######## check dictionary keys
            if field_check_name == 'question_field':
                if key_parts[-1] == 'button':
                    my_dict[f_key]['button'].append(add_item)
                if key_parts[-1] == 'allow':
                    my_dict[f_key].update({'allow':True})
                my_dict[f_key].update({'input':True})
            if key_parts[-1] == 'title':
                my_dict[f_key].update({'title':add_item})
                count+=1
                my_dict[f_key].update({'counter':count})
            elif key_parts[-1] == 'description':
                my_dict[f_key].update({'description':add_item})
            elif key_parts[-1] == 'image':
                my_dict[f_key].get('image').append(add_item)
            elif key_parts[-1] == 'youtube':
                my_dict[f_key].get('youtube').append(add_item)
            elif key_parts[-1] == 'url':
                my_dict[f_key].get('url').append(add_item)
            elif key_parts[-1] == 'values':
                my_dict[f_key].get('values').append(add_item)
            elif key_parts[-1] == 'select':
                if add_item == "on":
                    my_dict[f_key].update({'one_selection':True})
            elif key_parts[-1] == 'allow':
                if add_item == "on":
                    my_dict[f_key].update({'allow':True})
            elif key_parts[-1] == 'required':
                if add_item == "on":
                    my_dict[f_key].update({'required':True})
    # ######## returns an error if the image does not meet the standards
    if 'message' in check_image_upload_errors(request, form_pk, my_dict).keys():
        return check_image_upload_errors(request, form_pk, my_dict)['message']
    else:
        image_upload(request, pk, form_pk, my_dict)
    # ####### check None keys. If none, deletes that key
    for check_key, check_value in my_dict.items():
        for value_none in check_value.copy():
            if not check_value[value_none]:
                check_value.pop(value_none)
    return my_dict


def fill_form(request, pk, form_pk):
    form = request.data
    my_dict = {}
    
    for keys, val in form_pk.values.items():
        if keys not in my_dict:
            my_dict.update({keys:[]})
        ## check required keys and append to my_dict[keys]
        if 'required' in val.keys():
            my_dict[keys].append(True)
    for key, add_item in form.items():
        key_parts = key.split("_")
        field_name = "_".join(key_parts[:3])
        if field_name not in my_dict:
            message = 'Something went wrong'
            return Response({'error': message}, status=status.HTTP_406_NOT_ACCEPTABLE)
        if isinstance(add_item, list):
            for i in add_item:
                my_dict[field_name].append(i)
        else:
            my_dict[field_name].append(add_item)
    for i in my_dict.values():
        if True in i:
            if len(i) < 2:
                message = 'Required inputs cannot be empty'
                return Response({'error': message}, status=status.HTTP_406_NOT_ACCEPTABLE)
    print("my dict>", my_dict)
    return my_dict


def filled_form_to_xlsx(request, pk=None, wk=None):
    form = Form.objects.filter(id=pk).first()
    form_pk = FilledForms.objects.filter(id=wk).first()
    user = User.objects.filter(id=form_pk.person_id_id).first()
    print("name:", user.fullname)
    root = 'http://127.0.0.1:8000/'
    images_path = f'/static/media/{pk}/'
    xlsx_path = f'static/xlsx_files/filled_form/{pk}/'
    if not os.path.exists(xlsx_path):
        os.mkdir(xlsx_path)
    if " " in user.fullname:
        file_name = f'{user.id}_{user.fullname.replace(" ","_")}.xlsx'
    else:
        file_name = f'{user.id}_{user.fullname}.xlsx'

    workbook = xlsxwriter.Workbook(xlsx_path+file_name)
    worksheet = workbook.add_worksheet()
    cell_format = workbook.add_format({'bold': True, 'bg_color': 'blue', 'color':'white'})
    full = workbook.add_format({'bold': True, 'bg_color': 'green', 'color':'white'})
    null = workbook.add_format({'bold': True, 'bg_color': 'red', 'color':'white'})
    worksheet.set_column(0, 1, 10)
    worksheet.set_column(1, 1, 30)
    worksheet.set_column(2, 1, 30)
    worksheet.set_column(3, 1, 30)
    worksheet.set_column(4, 1, 30)
    worksheet.set_column(5, 1, 30)

    worksheet.write('A1', 'Counter', cell_format)
    worksheet.write('B1', 'Answer', cell_format)
    worksheet.write('C1', 'Values', cell_format)
    worksheet.write('D1', 'Button', cell_format)
    worksheet.write('E1', 'Title/Question', cell_format)
    worksheet.write('F1', 'Description', cell_format)
    worksheet.write('G1', 'Image url', cell_format)
    worksheet.write('H1', 'Uploaded Image', cell_format)
    worksheet.write('I1', 'Youtube Url', cell_format)
    worksheet.write('J1', 'Url', cell_format)
    worksheet.write('K1', 'Required', cell_format)
    
    for nums, (form_key, form_value) in enumerate(form.values.items(), 2):
        for filled_form_key, filled_form_value in form_pk.filled_form.items():
            if form_key == filled_form_key:
                ########## A line ##########
                if 'counter' in form_value:
                    worksheet.write(f'A{nums}', form_value['counter'])
                ########## B line ##########
                if filled_form_value:
                    answer_v = """"""
                    for answer in filled_form_value:
                        if type(answer) != bool:
                            answer_v += answer+'\n'
                    worksheet.write(f'B{nums}', answer_v, full)
                else:
                    worksheet.write(f'B{nums}', 'No answer was given', null)
                ########## C line ##########
                if 'values' in form_value:
                    values_v = """"""
                    for values in form_value['values']:
                        values_v += values+'\n'
                    worksheet.write(f'C{nums}', values_v)
                else:
                    worksheet.write(f'C{nums}', 'No value given', null)
                ########## D line ##########
                if 'button' in form_value:
                    button_v = """"""
                    for button in form_value['button']:
                        button_v += button+'\n'
                    worksheet.write(f'D{nums}', button_v)
                else:
                    worksheet.write(f'D{nums}', 'No value given', null)
                ########## E line ##########
                if 'title' in form_value:
                    worksheet.write(f'E{nums}', form_value['title'])
                ########## F line ##########
                if 'description' in form_value:
                    worksheet.write(f'F{nums}', form_value['description'])
                ########## G line ##########
                if 'image' in form_value:
                    image_v = """"""
                    for image in form_value['image']:
                        image_v += image+'\n'
                    worksheet.write(f'G{nums}', image_v)
                ########## H line##########
                if 'uploaded_image' in form_value:
                    for image in form_value['uploaded']:
                        worksheet.write(f'H{nums}', root+images_path+image)
                ########## I line ##########
                if 'youtube' in form_value:
                    youtube_v = """"""
                    for youtube in form_value['youtube']:
                        youtube_v += youtube+'\n'
                    worksheet.write(f'I{nums}', youtube_v)
                ########## J line ##########
                if 'url' in form_value:
                    url_v = """"""
                    for url in form_value['url']:
                        url_v += url+'\n'
                    worksheet.write(f'J{nums}', url_v)
                ########## K line ##########
                if 'required' in form_value:
                    worksheet.write(f'K{nums}', 'True') 
    workbook.close()
    download = root+xlsx_path+file_name
    return download