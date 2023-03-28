from rest_framework.decorators import APIView
from rest_framework import status
from rest_framework.response import Response
from .serializers import CreatePullSerializer, AnswerSerializer,ViewAnswerSerializer
from drf_yasg.utils import swagger_auto_schema
from own_forms.utils.check_auth import authorization
from auth2.models import User
from .models import Pull, PullAnswers
from .utils.helper import return_count


class Pulls(APIView):
    @swagger_auto_schema(operation_id="Pull", tags=['Pull'])
    def get(self, request):
        if authorization(request):
            return Response({'message':'Hi'})
    

class GetPull(APIView):
    @swagger_auto_schema(operation_id="Get Questionnarie", tags=['Pull'])
    def get(self, request, pk):
        if authorization(request):
            get_pull = Pull.objects.filter(id=pk).first()
            if get_pull:
                pull_answers = PullAnswers.objects.filter(pull_id_id=get_pull.id).all()
                check_user = PullAnswers.objects.filter(person_id_id=authorization(request)['id']).first()
                serializer = ViewAnswerSerializer(pull_answers, many=True)
                
                pull_context = {
                        'id':get_pull.id,
                        'Pull name':get_pull.pull_name,
                        'Anonimouse':get_pull.anonimouse,
                        'More_answers':get_pull.more_answers,
                        'Answers':return_count(get_pull)
                    }
                if check_user:
                    return Response({
                                        'pull_context':pull_context, 
                                    }, status=status.HTTP_200_OK)
                return Response({
                                    'pull_context':pull_context, 
                                    'data':serializer.data
                                }, status=status.HTTP_200_OK)
            else:
                return Response({'message':'Pull not found'}, status=status.HTTP_200_OK)
    

    @swagger_auto_schema(operation_id="Post Questionnarie", tags=['Pull'], request_body=AnswerSerializer)
    def post(self, request, pk):
        if authorization(request):
            user = User.objects.filter(id=authorization(request)['id']).first()
            get_pull = Pull.objects.filter(id=pk).first()
            if get_pull:
                pull_answers = PullAnswers.objects.filter(pull_id_id=get_pull.id).all()
                check_user = PullAnswers.objects.filter(pull_id_id=get_pull.id,person_id_id=authorization(request)['id']).first()
                if check_user:
                    return Response({'message':f'You have participated in the survey. Total survey participants: {len(pull_answers)}'})
                form = request.data
                for e in form['answer']:
                    if get_pull.more_answers == False and len(form['answer']) > 1:
                        return Response({'error':'This question can have only 1 answer'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
                    if e not in get_pull.answers.values():
                        return Response({'error':'Something went wrong'}, status=status.HTTP_405_METHOD_NOT_ALLOWED) 
                new_answer = PullAnswers.objects.create(person_id_id=user.id,
                                                        pull_id_id=get_pull.id,
                                                        answers=form['answer'])
                if get_pull.anonimouse == True:
                    if user.id == get_pull.owner_id_id:
                        pass
                    else:
                        return Response({'message':f'Thank you for participating in the survey.'}, status=status.HTTP_201_CREATED)
                new_answer.save()
                context = {
                    'Pull name':get_pull.pull_name,
                    'Your Answer':return_count(get_pull),
                    'Total survey participants':{len(pull_answers)}
                }
                return Response(context, status=status.HTTP_201_CREATED)
            else:
                return Response({'message':'Pull not found'}, status=status.HTTP_200_OK)
            

    @swagger_auto_schema(operation_id="Delete Pull", tags=['Pull'])
    def delete(self, request, pk):
        if authorization(request):
            user = User.objects.filter(id=authorization(request)['id']).first()
            get_pull = Pull.objects.filter(id=pk).first()
            if get_pull is None:
                return Response({'message':'Pull not found'}, status=status.HTTP_200_OK)
            if get_pull.owner_id_id == user.id:
                get_pull.delete()
                return Response({'message':f'{get_pull.pull_name} deleted'})
            else:
                return Response({"error":"You don't have permission"})
            

class CreateQuestionnaire(APIView):
    @swagger_auto_schema(operation_id="Create Questionnarie", tags=['Pull'], request_body=CreatePullSerializer)
    def post(self, request):
        if authorization(request):
            user = User.objects.filter(id=authorization(request)['id']).first()
            if user.company == True:
                form = request.data
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
                if check_pull_name:
                    return Response({"message":f"Form name '{form['pull_name']}' is available"})
                new_pull = Pull.objects.create(owner_id_id=user.id,
                                               pull_name=form['pull_name'],
                                               answers=form['answers'],
                                               anonimouse=form['anonimouse'],
                                               more_answers=form['more_answers']
                                               )
                new_pull.save()
                return Response({'created':{
                                    'Owner':user.email,
                                    'Pull name':form['pull_name'],
                                    'Anonimouse':form['anonimouse'],
                                    'More Answers':form['more_answers'],
                                    'Answers':form['answers']

                                }}, status=status.HTTP_201_CREATED)
            else:
                return Response({"error":"You don't have permission"}) 