import json
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse

class TestAvocadoEndPoint:
    endpoint = reverse('predict_price')

    def test_valid_get_data(self, supply_valid_data, supply_expected_output):
        
        response = APIClient().get(self.endpoint, supply_valid_data)

        assert response.status_code == status.HTTP_200_OK
        assert json.loads(response.content) == supply_expected_output


    def test_invalid_date_get_data(self, supply_invalid_date_field):
        response = APIClient().get(self.endpoint, supply_invalid_date_field)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_invalid_float_get_data(self, supply_invalid_float_field):
        response = APIClient().get(self.endpoint, supply_invalid_float_field)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_valid_post_data(self, supply_valid_data, supply_expected_output):
        response = APIClient().post(
            self.endpoint,
            data=supply_valid_data,
            format='json'
        )

        assert response.status_code == status.HTTP_200_OK
        assert json.loads(response.content) == supply_expected_output

    def test_invalid_date_post_data(self, supply_invalid_date_field):
        response = APIClient().post(
            self.endpoint,
            data=supply_invalid_date_field,
            format='json'
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_invalid_float_post_data(self, supply_invalid_float_field):
        response = APIClient().post(
            self.endpoint,
            data=supply_invalid_float_field,
            format='json'
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_invalid_json_post_data(self):
        response = APIClient().post(
            self.endpoint,
            data={'msg': 'invalid json'}
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert json.loads(response.content) == {'msg': 'Invalid json body format'}

