from rest_framework import serializers
from .models import TimeEntry
from projects.serializers import ProjectListSerializer


class TimeEntrySerializer(serializers.ModelSerializer):
    """
    Serializer for TimeEntry model.
    """
    user = serializers.ReadOnlyField(source='user.email')
    project_name = serializers.ReadOnlyField(source='project.name')
    client_name = serializers.ReadOnlyField(source='project.client.name')
    total_amount = serializers.ReadOnlyField()
    
    class Meta:
        model = TimeEntry
        fields = '__all__'
        read_only_fields = ('user', 'created_at', 'updated_at', 'total_amount')
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
    
    def validate_project(self, value):
        # Ensure the project belongs to the current user
        if value.user != self.context['request'].user:
            raise serializers.ValidationError("You can only log time for your own projects.")
        return value
    
    def validate_date(self, value):
        from django.utils import timezone
        if value > timezone.now().date():
            raise serializers.ValidationError("Time entries cannot be logged for future dates.")
        return value


class TimeEntryListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing time entries with summary information.
    """
    project_name = serializers.ReadOnlyField(source='project.name')
    client_name = serializers.ReadOnlyField(source='project.client.name')
    total_amount = serializers.ReadOnlyField()
    
    class Meta:
        model = TimeEntry
        fields = ('id', 'project_name', 'client_name', 'date', 'hours', 'hourly_rate', 
                 'total_amount', 'description', 'is_billable', 'created_at')


class TimeEntryDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed time entry view with project information.
    """
    project = ProjectListSerializer(read_only=True)
    total_amount = serializers.ReadOnlyField()
    
    class Meta:
        model = TimeEntry
        fields = '__all__'
        read_only_fields = ('user', 'created_at', 'updated_at', 'total_amount')


class TimeEntryBulkCreateSerializer(serializers.Serializer):
    """
    Serializer for bulk creating time entries.
    """
    time_entries = TimeEntrySerializer(many=True)
    
    def create(self, validated_data):
        time_entries_data = validated_data.pop('time_entries')
        time_entries = []
        
        for entry_data in time_entries_data:
            entry_data['user'] = self.context['request'].user
            time_entry = TimeEntry.objects.create(**entry_data)
            time_entries.append(time_entry)
        
        return {'time_entries': time_entries} 