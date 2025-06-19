import stripe
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import StripePaymentIntent, StripeWebhookEvent
from invoices.services.invoice_service import InvoiceService

# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeService:
    """
    Service for Stripe payment processing.
    """
    
    @staticmethod
    def create_payment_intent(invoice, user):
        """
        Create a Stripe payment intent for an invoice.
        """
        try:
            # Create payment intent
            payment_intent = stripe.PaymentIntent.create(
                amount=int(invoice.total_amount * 100),  # Convert to cents
                currency=invoice.client.currency.lower(),
                metadata={
                    'invoice_id': invoice.id,
                    'invoice_number': invoice.invoice_number,
                    'user_id': user.id,
                    'client_id': invoice.client.id
                },
                payment_method_types=['card'],
                description=f"Payment for invoice {invoice.invoice_number}"
            )
            
            # Save to database
            stripe_payment_intent = StripePaymentIntent.objects.create(
                user=user,
                invoice=invoice,
                payment_intent_id=payment_intent.id,
                amount=invoice.total_amount,
                currency=invoice.client.currency.lower(),
                status=payment_intent.status,
                client_secret=payment_intent.client_secret,
                payment_method_types=payment_intent.payment_method_types,
                metadata=payment_intent.metadata
            )
            
            return stripe_payment_intent
            
        except stripe.error.StripeError as e:
            raise Exception(f"Stripe error: {str(e)}")
    
    @staticmethod
    def get_payment_intent(payment_intent_id):
        """
        Retrieve a payment intent from Stripe.
        """
        try:
            return stripe.PaymentIntent.retrieve(payment_intent_id)
        except stripe.error.StripeError as e:
            raise Exception(f"Stripe error: {str(e)}")
    
    @staticmethod
    def process_webhook_event(event_data, event_type):
        """
        Process a Stripe webhook event.
        """
        try:
            # Save webhook event
            webhook_event = StripeWebhookEvent.objects.create(
                event_id=event_data['id'],
                event_type=event_type,
                event_data=event_data
            )
            
            # Process based on event type
            if event_type == 'payment_intent.succeeded':
                StripeService._handle_payment_success(event_data)
            elif event_type == 'payment_intent.payment_failed':
                StripeService._handle_payment_failure(event_data)
            
            # Mark as processed
            webhook_event.processed = True
            webhook_event.save()
            
            return webhook_event
            
        except Exception as e:
            if webhook_event:
                webhook_event.error_message = str(e)
                webhook_event.save()
            raise e
    
    @staticmethod
    def _handle_payment_success(event_data):
        """
        Handle successful payment.
        """
        payment_intent_id = event_data['data']['object']['id']
        
        try:
            # Find our payment intent record
            stripe_payment_intent = StripePaymentIntent.objects.get(
                payment_intent_id=payment_intent_id
            )
            
            # Mark invoice as paid
            InvoiceService.mark_as_paid(
                invoice=stripe_payment_intent.invoice,
                payment_method='stripe',
                stripe_payment_intent_id=payment_intent_id
            )
            
        except StripePaymentIntent.DoesNotExist:
            raise Exception(f"Payment intent {payment_intent_id} not found in database")
    
    @staticmethod
    def _handle_payment_failure(event_data):
        """
        Handle failed payment.
        """
        payment_intent_id = event_data['data']['object']['id']
        
        try:
            # Find our payment intent record
            stripe_payment_intent = StripePaymentIntent.objects.get(
                payment_intent_id=payment_intent_id
            )
            
            # Update status
            stripe_payment_intent.status = 'failed'
            stripe_payment_intent.save()
            
        except StripePaymentIntent.DoesNotExist:
            raise Exception(f"Payment intent {payment_intent_id} not found in database")
    
    @staticmethod
    def create_checkout_session(invoice, user, success_url, cancel_url):
        """
        Create a Stripe checkout session for an invoice.
        """
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': invoice.client.currency.lower(),
                        'product_data': {
                            'name': f'Invoice {invoice.invoice_number}',
                            'description': f'Payment for invoice {invoice.invoice_number}',
                        },
                        'unit_amount': int(invoice.total_amount * 100),
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=success_url,
                cancel_url=cancel_url,
                metadata={
                    'invoice_id': invoice.id,
                    'invoice_number': invoice.invoice_number,
                    'user_id': user.id,
                    'client_id': invoice.client.id
                }
            )
            
            return session
            
        except stripe.error.StripeError as e:
            raise Exception(f"Stripe error: {str(e)}") 