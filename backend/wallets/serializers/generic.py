from rest_framework import serializers

class CommaSeparatedIntegerListField(serializers.ListField):
    def to_internal_value(self, data):
        data = data[0].split(',')
        return super().to_internal_value(data)