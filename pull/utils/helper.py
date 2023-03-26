from rest_framework import status
from rest_framework.response import Response
from ..models import Pull


def check_errors(request, form):
    form_keys = ['pull_name','answers','anonimouse','more_answers']
    request_keys = []
    for k in form.keys():
        if k not in form_keys:
            return Response({'message':'Something went wrong'}, status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
        request_keys.append(k)
    if len(form_keys) != len(request_keys):
        return Response({'message':'Something went wrong'}, status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
    check_unique_answer = []
    for answer in request.data['answers'].values():
        if answer in check_unique_answer:
            return Response({'error':f'The answer "{answer}" are repeated'}, status=status.HTTP_200_OK)
        check_unique_answer.append(answer)
    if len(check_unique_answer) > 10:
        return Response({'error':'I can post a maximum of 10 answers'}, status=status.HTTP_200_OK)
    check_pull_name = Pull.objects.filter(pull_name=form['pull_name']).first()
    print(">>>>>", check_pull_name)
    if check_pull_name:
        return Response({"message":f"Form name '{form['pull_name']}' is available"})