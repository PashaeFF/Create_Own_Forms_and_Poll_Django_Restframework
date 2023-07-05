from rest_framework.decorators import APIView
from rest_framework import status
from rest_framework.response import Response
from .serializers import CreatePollSerializer, AnswerSerializer,ViewAnswerSerializer
from drf_yasg.utils import swagger_auto_schema
from own_forms.utils.check_auth import authorization
from auth2.models import User
from .models import Poll, PollAnswers
from .utils.helper import return_count


class Polls(APIView):
    @swagger_auto_schema(operation_id="Poll", tags=['Poll'])
    def get(self, request):
        if authorization(request):
            return Response({'message':'Hi'})
    

class GetPoll(APIView):
    @swagger_auto_schema(operation_id="Get Questionnarie", tags=['Poll'])
    def get(self, request, pk):
        if authorization(request):
            get_poll = Poll.objects.filter(id=pk).first()
            if get_poll:
                poll_answers = PollAnswers.objects.filter(poll_id_id=get_poll.id).all()
                check_user = PollAnswers.objects.filter(person_id_id=authorization(request)['id']).first()
                serializer = ViewAnswerSerializer(poll_answers, many=True)
                
                poll_context = {
                        'id':get_poll.id,
                        'Poll name':get_poll.poll_name,
                        'Anonimouse':get_poll.anonimouse,
                        'More_answers':get_poll.more_answers,
                        'Answers':return_count(get_poll)
                    }
                if check_user:
                    return Response({
                                        'poll_context':poll_context, 
                                    }, status=status.HTTP_200_OK)
                return Response({
                                    'poll_context':poll_context, 
                                    'data':serializer.data
                                }, status=status.HTTP_200_OK)
            else:
                return Response({'message':'Poll not found'}, status=status.HTTP_200_OK)
    

    @swagger_auto_schema(operation_id="Post Questionnarie", tags=['Poll'], request_body=AnswerSerializer)
    def post(self, request, pk):
        if authorization(request):
            user = User.objects.filter(id=authorization(request)['id']).first()
            get_poll = Poll.objects.filter(id=pk).first()
            if get_poll:
                poll_answers = PollAnswers.objects.filter(poll_id_id=get_poll.id).all()
                check_user = PollAnswers.objects.filter(poll_id_id=get_poll.id,person_id_id=authorization(request)['id']).first()
                if check_user:
                    return Response({'message':f'You have participated in the survey. Total survey participants: {len(poll_answers)}'})
                form = request.data
                for e in form['answer']:
                    if get_poll.more_answers == False and len(form['answer']) > 1:
                        return Response({'error':'This question can have only 1 answer'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
                    if e not in get_poll.answers.values():
                        return Response({'error':'Something went wrong'}, status=status.HTTP_405_METHOD_NOT_ALLOWED) 
                new_answer = PollAnswers.objects.create(person_id_id=user.id,
                                                        poll_id_id=get_poll.id,
                                                        answers=form['answer'])
                if get_poll.anonimouse == True:
                    if user.id == get_poll.owner_id_id:
                        pass
                    else:
                        return Response({'message':f'Thank you for participating in the survey.'}, status=status.HTTP_201_CREATED)
                new_answer.save()
                context = {
                    'Poll name':get_poll.poll_name,
                    'Your Answer':return_count(get_poll),
                    'Total survey participants':{len(poll_answers)}
                }
                return Response(context, status=status.HTTP_201_CREATED)
            else:
                return Response({'message':'Poll not found'}, status=status.HTTP_200_OK)
            

    @swagger_auto_schema(operation_id="Delete Poll", tags=['Poll'])
    def delete(self, request, pk):
        if authorization(request):
            user = User.objects.filter(id=authorization(request)['id']).first()
            get_poll = Poll.objects.filter(id=pk).first()
            if get_poll is None:
                return Response({'message':'Poll not found'}, status=status.HTTP_200_OK)
            if get_poll.owner_id_id == user.id:
                get_poll.delete()
                return Response({'message':f'{get_poll.poll_name} deleted'})
            else:
                return Response({"error":"You don't have permission"})
            

class CreateQuestionnaire(APIView):
    @swagger_auto_schema(operation_id="Create Questionnarie", tags=['Poll'], request_body=CreatePollSerializer)
    def post(self, request):
        if authorization(request):
            user = User.objects.filter(id=authorization(request)['id']).first()
            if user.company == True:
                form = request.data
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
                if check_poll_name:
                    return Response({"message":f"Form name '{form['poll_name']}' is available"})
                new_poll = Poll.objects.create(owner_id_id=user.id,
                                               poll_name=form['poll_name'],
                                               answers=form['answers'],
                                               anonimouse=form['anonimouse'],
                                               more_answers=form['more_answers']
                                               )
                new_poll.save()
                return Response({'created':{
                                    'Owner':user.email,
                                    'Poll name':form['poll_name'],
                                    'Anonimouse':form['anonimouse'],
                                    'More Answers':form['more_answers'],
                                    'Answers':form['answers']

                                }}, status=status.HTTP_201_CREATED)
            else:
                return Response({"error":"You don't have permission"}) 