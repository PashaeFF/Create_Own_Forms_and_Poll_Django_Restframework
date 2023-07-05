from rest_framework import status
from rest_framework.response import Response
from ..models import Poll, PollAnswers


def check_errors(request, form):
    form_keys = ['poll_name','answers','anonimouse','more_answers']
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
    check_poll_name = Poll.objects.filter(poll_name=form['poll_name']).first()
    print(">>>>>", check_poll_name)
    if check_poll_name:
        return Response({"message":f"Form name '{form['poll_name']}' is available"})
    

def return_count(get_poll):
    poll_answers = PollAnswers.objects.filter(poll_id_id=get_poll.id).all()
    poll_length = len(poll_answers)
    count = 1
    my_dict= {}
    for e in get_poll.answers.values():
        for i in poll_answers.values():
            for j in i['answers']:
                if e == j:
                    if e in my_dict.keys():
                        my_dict[e].update({'answer':e, 'count':my_dict[e]['count']+1})
                    else:
                        my_dict[e] = {'answer':e, 'count':count}
    return my_dict


def check_anonimouse():
    return ''