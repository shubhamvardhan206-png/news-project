from .models import Payment
from django.db.models import Q


def get_user_payments(user):
    """
    Get all payments for a specific user
    """
    return Payment.objects.filter(user=user).order_by('-created_at')


def get_user_completed_payments(user):
    """
    Get completed payments for a user
    """
    return Payment.objects.filter(
        user=user,
        status='completed'
    ).order_by('-created_at')


def get_user_pending_payments(user):
    """
    Get pending payments for a user
    """
    return Payment.objects.filter(
        user=user,
        status='pending'
    ).order_by('-created_at')


def get_payment_by_transaction_id(transaction_id):
    """
    Get payment by transaction ID
    """
    try:
        return Payment.objects.get(transaction_id=transaction_id)
    except Payment.DoesNotExist:
        return None


def get_user_payment_summary(user):
    """
    Get payment summary for a user
    """
    payments = Payment.objects.filter(user=user)
    
    return {
        'total_payments': payments.count(),
        'completed_payments': payments.filter(status='completed').count(),
        'pending_payments': payments.filter(status='pending').count(),
        'failed_payments': payments.filter(status='failed').count(),
        'total_amount_paid': sum(p.final_amount for p in payments.filter(status='completed')),
        'total_discount_received': sum(p.discount_amount for p in payments.filter(status='completed')),
    }


def search_payments(user, query):
    """
    Search payments by transaction ID or plan name
    """
    return Payment.objects.filter(user=user).filter(
        Q(transaction_id__icontains=query) |
        Q(plan__name__icontains=query)
    ).order_by('-created_at')