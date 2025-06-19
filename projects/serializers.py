from rest_framework import serializers
from .models import Project
from clients.serializers import ClientSerializer


class ProjectSerializer(serializers.ModelSerializer):
    """
    Serializer for Project model.
    """
    user = serializers.ReadOnlyField(source='user.email')
    client_name = serializers.ReadOnlyField(source='client.name')
    total_hours = serializers.ReadOnlyField()
    total_billed = serializers.ReadOnlyField()
    is_over_budget = serializers.ReadOnlyField()
    
    class Meta:
        model = Project
        fields = '__all__'
        read_only_fields = ('user', 'created_at', 'updated_at', 'total_hours', 'total_billed', 'is_over_budget')
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
    
    def validate_client(self, value):
        # Ensure the client belongs to the current user
        if value.user != self.context['request'].user:
            raise serializers.ValidationError("You can only assign projects to your own clients.")
        return value


class ProjectListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing projects with summary information.
    """
    client_name = serializers.ReadOnlyField(source='client.name')
    client_company = serializers.ReadOnlyField(source='client.company_name')
    total_hours = serializers.ReadOnlyField()
    total_billed = serializers.ReadOnlyField()
    is_over_budget = serializers.ReadOnlyField()
    
    class Meta:
        model = Project
        fields = ('id', 'name', 'client_name', 'client_company', 'status', 'hourly_rate', 
                 'total_hours', 'total_billed', 'is_over_budget', 'auto_invoice', 'created_at')


class ProjectDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed project view with client information.
    """
    client = ClientSerializer(read_only=True)
    total_hours = serializers.ReadOnlyField()
    total_billed = serializers.ReadOnlyField()
    is_over_budget = serializers.ReadOnlyField()
    
    class Meta:
        model = Project
        fields = '__all__'
        read_only_fields = ('user', 'created_at', 'updated_at', 'total_hours', 'total_billed', 'is_over_budget') 