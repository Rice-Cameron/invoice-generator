import stripe
import json
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import HttpResponse
from django.conf import settings
from .models import StripePaymentIntent, StripeWebhookEvent
from .serializers import (
    StripePaymentIntentSerializer,
    CreatePaymentIntentSerializer,
    CreateCheckoutSessionSerializer
)
from .services import StripeService

# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


class StripePaymentIntentListView(generics.ListAPIView):
    """
    View for listing Stripe payment intents.
    """
    serializer_class = StripePaymentIntentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return StripePaymentIntent.objects.filter(user=self.request.user).select_related('invoice', 'invoice__client')


class CreatePaymentIntentView(generics.CreateAPIView):
    """
    View for creating Stripe payment intents.
    """
    serializer_class = CreatePaymentIntentSerializer
    permission_classes = [IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        invoice = serializer.validated_data['invoice_id']
        
        try:
            payment_intent = StripeService.create_payment_intent(invoice, request.user)
            
            return Response({
                'payment_intent': StripePaymentIntentSerializer(payment_intent, context={'request': request}).data,
                'client_secret': payment_intent.client_secret
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CreateCheckoutSessionView(generics.CreateAPIView):
    """
    View for creating Stripe checkout sessions.
    """
    serializer_class = CreateCheckoutSessionSerializer
    permission_classes = [IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        invoice = serializer.validated_data['invoice_id']
        success_url = serializer.validated_data['success_url']
        cancel_url = serializer.validated_data['cancel_url']
        
        try:
            session = StripeService.create_checkout_session(invoice, request.user, success_url, cancel_url)
            
            return Response({
                'session_id': session.id,
                'url': session.url
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_payment_intent_status(request, payment_intent_id):
    """
    View for getting payment intent status.
    """
    try:
        payment_intent = StripeService.get_payment_intent(payment_intent_id)
        
        return Response({
            'payment_intent_id': payment_intent.id,
            'status': payment_intent.status,
            'amount': payment_intent.amount / 100,  # Convert from cents
            'currency': payment_intent.currency
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
@require_POST
def stripe_webhook(request):
    """
    Webhook endpoint for Stripe events.
    """
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    try:
        # Verify webhook signature
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
        
        # Process the event
        StripeService.process_webhook_event(event.data, event.type)
        
        return HttpResponse(status=200)
        
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)
    except Exception as e:
        # Other errors
        return HttpResponse(status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def stripe_config(request):
    """
    View for getting Stripe configuration (publishable key).
    """
    return Response({
        'publishable_key': settings.STRIPE_PUBLISHABLE_KEY
    }) 