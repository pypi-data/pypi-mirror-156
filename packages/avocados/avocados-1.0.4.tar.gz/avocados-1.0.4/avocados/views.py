from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from avocados.serializers import AvocadoSerializer
from rest_framework.parsers import JSONParser
from rest_framework.exceptions import ParseError
from rest_framework import status
from avocados import predictor

@csrf_exempt
def predict_price(request):
    if request.method == 'GET':
        data = request.GET.dict()

    elif request.method == 'POST':
        try:
            data = JSONParser().parse(request)
        except ParseError:
            return JsonResponse({'msg': 'Invalid json body format'}, status=status.HTTP_400_BAD_REQUEST)

    serializer = AvocadoSerializer(data=data)
    if serializer.is_valid():
        average_price = predictor.predict(**serializer.data)
        data['average_price'] = average_price
        serializer = AvocadoSerializer(data=data)
        serializer.is_valid()
        return JsonResponse(serializer.data, status=status.HTTP_200_OK)
    else:
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)