from rest_framework.decorators import APIView
from rest_framework import status
from rest_framework.response import Response
from .serializers import CreatePullSerializer, AnswerSerializer
from drf_yasg.utils import swagger_auto_schema
from own_forms.utils.check_auth import authorization
from auth2.models import User
from .models import Pull


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
                return Response({
                            'id':get_pull.id,
                            'Pull name':get_pull.pull_name,
                            'Anonimouse':get_pull.anonimouse,
                            'More_answers':get_pull.more_answers,
                            'Answers':get_pull.answers
                            }, status=status.HTTP_200_OK)
            else:
                return Response({'message':'Pull not found'}, status=status.HTTP_200_OK)
    

    @swagger_auto_schema(operation_id="Post Questionnarie", tags=['Pull'], request_body=AnswerSerializer)
    def post(self, request, pk):
        if authorization(request):
            user = User.objects.filter(id=authorization(request)['id']).first()
            get_pull = Pull.objects.filter(id=pk).first()
            if get_pull:
                form = request.data
                for e in form['answer']:
                    if e not in get_pull.answers.values():
                        return Response({'error':'Something went wrong'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
                context = {
                    'Pull name':get_pull.pull_name,
                    'Answers':get_pull.answers,
                    'Your Answer':form['answer']
                }
                return Response(context, status=status.HTTP_201_CREATED)
            else:
                return Response({'message':'Pull not found'}, status=status.HTTP_200_OK)
            

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
                                    'More Answers':form['more_answers']

                                }}, status=status.HTTP_201_CREATED)
            else:
                return Response({"error":"You don't have permission"})
            
    
