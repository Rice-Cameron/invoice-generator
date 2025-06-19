from rest_framework import serializers
from .models import Client
from django.db import models


class ClientSerializer(serializers.ModelSerializer):
    """
    Serializer for Client model.
    """
    user = serializers.ReadOnlyField(source='user.email')
    
    class Meta:
        model = Client
        fields = '__all__'
        read_only_fields = ('user', 'created_at', 'updated_at')
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class ClientListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing clients with summary information.
    """
    project_count = serializers.SerializerMethodField()
    total_billed = serializers.SerializerMethodField()
    
    class Meta:
        model = Client
        fields = ('id', 'name', 'company_name', 'email', 'is_active', 
                 'recurring_invoice', 'project_count', 'total_billed', 'created_at')
    
    def get_project_count(self, obj):
        return obj.projects.count()
    
    def get_total_billed(self, obj):
        total = Invoice.objects.filter(client=obj, status='paid').aggregate(
            total=models.Sum('total_amount')
        )['total']
        return float(total) if total else 0.0 