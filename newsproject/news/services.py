from .models import Payment, Coupon
from django.utils import timezone

def verify_payment_integrity(transaction_id):
    """
    Check if transaction ID already exists in database
    Returns True if it exists (duplicate), False if new
    """
    return Payment.objects.filter(transaction_id=transaction_id).exists()


def create_payment_record(user, transaction_id, amount, coupon=None):
    """
    Create a payment record in database
    
    Args:
        user: User object
        transaction_id: Unique transaction ID
        amount: Final amount after discount
        coupon: Coupon object (optional)
    
    Returns:
        Payment object
    """
    # Calculate discount if coupon is provided
    discount = 0
    if coupon:
        coupon.times_used += 1
        coupon.save()
        # Calculate discount amount based on coupon type
        if coupon.discount_percent:
            discount = (amount / (100 - coupon.discount_percent)) * coupon.discount_percent
        elif coupon.discount_amount:
            discount = coupon.discount_amount
    
    original_amount = amount + discount
    
    payment = Payment.objects.create(
        user=user,
        transaction_id=transaction_id,
        amount=original_amount,
        discount_amount=discount,
        final_amount=amount,
        status='completed',
        payment_method='UPI',
        coupon=coupon
    )
    
    return payment


def validate_coupon(coupon_code, plan=None):
    """
    Validate a coupon code
    
    Returns:
        (is_valid, coupon_obj, error_message)
    """
    try:
        coupon = Coupon.objects.get(code=coupon_code)
    except Coupon.DoesNotExist:
        return False, None, "Coupon code does not exist"
    
    if not coupon.is_active:
        return False, coupon, "Coupon is inactive"
    
    if coupon.is_expired():
        return False, coupon, "Coupon has expired"
    
    if coupon.max_uses and coupon.times_used >= coupon.max_uses:
        return False, coupon, "Coupon usage limit reached"
    
    if plan and not coupon.can_apply_to_plan(plan):
        return False, coupon, "Coupon is not applicable to this plan"
    
    return True, coupon, None


def calculate_discount(amount, coupon):
    """
    Calculate discount amount from coupon
    
    Args:
        amount: Original amount
        coupon: Coupon object
    
    Returns:
        Discount amount
    """
    if not coupon:
        return 0
    
    if coupon.discount_percent:
        return (amount * coupon.discount_percent) / 100
    elif coupon.discount_amount:
        return min(coupon.discount_amount, amount)  # Don't exceed original amount
    
    return 0


def get_final_amount(original_amount, coupon=None):
    """
    Get final amount after applying coupon
    
    Returns:
        (final_amount, discount_amount)
    """
    discount = calculate_discount(original_amount, coupon)
    final_amount = original_amount - discount
    return final_amount, discount