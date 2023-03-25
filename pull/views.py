from rest_framework.decorators import APIView
from rest_framework.response import Response
from .serializers import CreatePullSerializer
from drf_yasg.utils import swagger_auto_schema
from own_forms.utils.check_auth import authorization


class Pull(APIView):
    @swagger_auto_schema(operation_id="Pull", tags=['Pull'])
    def get(self, request):
        if authorization(request):
            return Response({'message':'Hi'})
    
    
class CreateQuestionnaire(APIView):
    @swagger_auto_schema(operation_id="Create Questionnarie", tags=['Pull'], request_body=CreatePullSerializer)
    def post(self, request):
        if authorization(request):
            return Response({'message':'Pull created'})