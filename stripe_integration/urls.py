from django.urls import path
from .views import (
    StripePaymentIntentListView,
    CreatePaymentIntentView,
    CreateCheckoutSessionView,
    get_payment_intent_status,
    stripe_webhook,
    stripe_config
)

urlpatterns = [
    path('payment-intents/', StripePaymentIntentListView.as_view(), name='stripe-payment-intent-list'),
    path('create-payment-intent/', CreatePaymentIntentView.as_view(), name='stripe-create-payment-intent'),
    path('create-checkout-session/', CreateCheckoutSessionView.as_view(), name='stripe-create-checkout-session'),
    path('payment-intent-status/<str:payment_intent_id>/', get_payment_intent_status, name='stripe-payment-intent-status'),
    path('webhook/', stripe_webhook, name='stripe-webhook'),
    path('config/', stripe_config, name='stripe-config'),
] 