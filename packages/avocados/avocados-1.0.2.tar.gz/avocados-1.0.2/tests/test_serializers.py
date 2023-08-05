from avocados.serializers import AvocadoSerializer
from conftest import supply_valid_data

class TestAvocadoSerializer:
    def test_valid_serialized_data(self, supply_valid_data):
        serializer = AvocadoSerializer(data=supply_valid_data)

        assert serializer.is_valid(raise_exception=True)
        assert len(serializer.errors) == 0

    def test_invalid_date_serialized_data(self, supply_invalid_date_field):        
        serializer = AvocadoSerializer(data=supply_invalid_date_field)

        serializer.is_valid()
        assert len(serializer.errors) != 0

    def test_invalid_float_serialized_data(self, supply_invalid_float_field):
        serializer = AvocadoSerializer(data=supply_invalid_float_field)

        serializer.is_valid()
        assert len(serializer.errors) != 0