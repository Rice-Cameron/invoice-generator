from rest_framework import serializers
from .models import Invoice, InvoiceItem
from clients.serializers import ClientSerializer
from projects.serializers import ProjectListSerializer


class InvoiceItemSerializer(serializers.ModelSerializer):
    """
    Serializer for InvoiceItem model.
    """
    class Meta:
        model = InvoiceItem
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class InvoiceSerializer(serializers.ModelSerializer):
    """
    Serializer for Invoice model.
    """
    user = serializers.ReadOnlyField(source='user.email')
    client_name = serializers.ReadOnlyField(source='client.name')
    project_name = serializers.ReadOnlyField(source='project.name')
    items = InvoiceItemSerializer(many=True, read_only=True)
    is_overdue = serializers.ReadOnlyField()
    days_overdue = serializers.ReadOnlyField()
    
    class Meta:
        model = Invoice
        fields = '__all__'
        read_only_fields = ('user', 'created_at', 'updated_at', 'invoice_number', 'is_overdue', 'days_overdue')
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
    
    def validate_client(self, value):
        # Ensure the client belongs to the current user
        if value.user != self.context['request'].user:
            raise serializers.ValidationError("You can only create invoices for your own clients.")
        return value
    
    def validate_project(self, value):
        if value and value.user != self.context['request'].user:
            raise serializers.ValidationError("You can only assign your own projects to invoices.")
        return value


class InvoiceListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing invoices with summary information.
    """
    client_name = serializers.ReadOnlyField(source='client.name')
    project_name = serializers.ReadOnlyField(source='project.name')
    is_overdue = serializers.ReadOnlyField()
    days_overdue = serializers.ReadOnlyField()
    
    class Meta:
        model = Invoice
        fields = ('id', 'invoice_number', 'client_name', 'project_name', 'issue_date', 
                 'due_date', 'total_amount', 'status', 'is_overdue', 'days_overdue', 'created_at')


class InvoiceDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed invoice view with all related information.
    """
    client = ClientSerializer(read_only=True)
    project = ProjectListSerializer(read_only=True)
    items = InvoiceItemSerializer(many=True, read_only=True)
    is_overdue = serializers.ReadOnlyField()
    days_overdue = serializers.ReadOnlyField()
    
    class Meta:
        model = Invoice
        fields = '__all__'
        read_only_fields = ('user', 'created_at', 'updated_at', 'invoice_number', 'is_overdue', 'days_overdue')


class InvoiceCreateFromTimeEntriesSerializer(serializers.Serializer):
    """
    Serializer for creating invoices from time entries.
    """
    client = serializers.PrimaryKeyRelatedField(queryset=None)
    project = serializers.PrimaryKeyRelatedField(queryset=None, required=False, allow_null=True)
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    issue_date = serializers.DateField(required=False)
    due_date = serializers.DateField(required=False)
    tax_rate = serializers.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    discount_rate = serializers.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    notes = serializers.CharField(required=False, allow_blank=True)
    terms_conditions = serializers.CharField(required=False, allow_blank=True)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set querysets based on the current user
        if 'context' in kwargs and 'request' in kwargs['context']:
            user = kwargs['context']['request'].user
            self.fields['client'].queryset = user.clients.all()
            self.fields['project'].queryset = user.projects.all()
    
    def validate(self, attrs):
        if attrs['start_date'] > attrs['end_date']:
            raise serializers.ValidationError("Start date must be before end date.")
        return attrs


class InvoiceSendSerializer(serializers.Serializer):
    """
    Serializer for sending invoices via email.
    """
    email_subject = serializers.CharField(max_length=255, required=False)
    email_message = serializers.CharField(required=False, allow_blank=True)
    send_to_client = serializers.BooleanField(default=True)
    send_copy_to_user = serializers.BooleanField(default=False) 