import os, uuid
from collections import Counter
from PIL import Image


######### CHECK IMAGE ERRORS #########
def check_image_upload_errors(request, form_pk, my_dict):
    image_keys_list = []
    for file_key, file_item in request.FILES.items():
        fileitem = request.FILES[file_key]
        extension = fileitem.name.split('.')[-1]
        image_extensions = ['jpeg','jpg','png']
        if fileitem.size > 8388608:
            size = str(fileitem.size/1000000).split(".")
            message = f'The picture is too big (Picture size: {size[0]}.{size[1][0]} mb)'
            return {'message':{'error':message}}
        if extension not in image_extensions:
            message = 'Only "jpg", "jpeg", "png" images are allowed'
            return {'message':{'error':message}}
        fileitem = request.FILES[file_key]
        print("file item", file_item)
        files_key_parts = file_key.split("_")
        print("key part", files_key_parts)
        files_field_name = "_".join(files_key_parts[:3])
        last_field_name = "_".join(files_key_parts[-2:])
        extension = fileitem.name.split('.')[-1]
        if fileitem.name:
            if last_field_name == 'uploaded_image':
                image_keys_list.append(files_field_name)
    image_count_checker = Counter(image_keys_list)
    for count in image_count_checker.values():
        if count > 1:
            return {'message':{'error':'1 box can contain a maximum of one image'}}
    return {'uploaded_image':image_keys_list}


######## UPLOAD AND COMPRESS IMAGE ########
def image_upload(request, pk, form_pk, my_dict):
    image_path = f'static/media/{pk}'
    if os.path.exists(f'static/media/{pk}'):
        pass
    else:
        os.mkdir(f'static/media/{pk}/')
    for file_key in request.FILES.keys():
        fileitem = request.FILES[file_key]
        files_key_parts = file_key.split("_")
        files_field_name = "_".join(files_key_parts[:3])
        last_field_name = "_".join(files_key_parts[-2:])
        extension = fileitem.name.split('.')[-1]
        if fileitem.name:
            image = Image.open(fileitem.file)
            print(f"Image original size: {image.size}")
            image_name = f'{uuid.uuid4()}.{extension}'
            ####### if the size of the image is larger than 400kb, it degrades its quality
            if fileitem.size < 400000:
                image.save(f'{image_path}/{image_name}', optimize = True, quality = 100)
            elif 1000000 > fileitem.size > 400000:
                image.save(f'{image_path}/{image_name}', optimize = True, quality = 40)
            elif 3000000 > fileitem.size > 1000000:
                image.save(f'{image_path}/{image_name}', optimize = True, quality = 20)
            elif 5000000 > fileitem.size > 3000000:
                image.save(f'{image_path}/{image_name}', optimize = True, quality = 11)
            elif 8388608 > fileitem.size > 5000000:
                image.save(f'{image_path}/{image_name}', optimize = True, quality = 7)
            # if 'uploaded_image' not in my_dict[files_field_name].keys():
            #     my_dict[files_field_name] = {'uploaded_image':[]}
            # else:
            if last_field_name == 'uploaded_image':
                my_dict[files_field_name].get('uploaded_image').append(image_name)
