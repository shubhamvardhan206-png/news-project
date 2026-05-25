"""
Transaction handling utilities for filtering and exporting payment data
"""
from datetime import datetime, timedelta
from django.utils import timezone
from django.http import HttpResponse
from .models import Payment
import csv
import io

class TransactionManager:
    """Manages transaction filtering by time period"""
    
    PERIOD_CHOICES = {
        'week': 7,
        'month': 30,
        'year': 365,
        'all': None,
    }

    @staticmethod
    def get_date_range(period):
        """Get start and end dates for a given period"""
        now = timezone.now()
        
        if period == 'week':
            start_date = now - timedelta(days=7)
        elif period == 'month':
            start_date = now - timedelta(days=30)
        elif period == 'year':
            start_date = now - timedelta(days=365)
        else:
            start_date = None
        
        return start_date, now

    @staticmethod
    def filter_transactions(queryset, period='all'):
        """Filter transactions by period"""
        if period == 'all':
            return queryset
        
        start_date, end_date = TransactionManager.get_date_range(period)
        return queryset.filter(created_at__range=[start_date, end_date])

    @staticmethod
    def get_transaction_stats(transactions):
        """Calculate statistics for transactions"""
        if not transactions.exists():
            return {
                'count': 0,
                'total': 0,
                'completed': 0,
                'pending': 0,
                'failed': 0,
                'total_discount': 0,
                'average': 0,
            }
        
        completed = transactions.filter(status='completed')
        total_completed = sum([p.final_amount for p in completed])
        
        stats = {
            'count': transactions.count(),
            'total': total_completed,
            'completed': completed.count(),
            'pending': transactions.filter(status='pending').count(),
            'failed': transactions.filter(status='failed').count(),
            'total_discount': sum([p.discount_amount for p in completed]),
            'average': total_completed / completed.count() if completed.count() > 0 else 0,
        }
        return stats

    @staticmethod
    def export_to_csv(transactions, period='all'):
        """Export transactions to CSV format"""
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow([
            'Transaction ID',
            'User',
            'Plan',
            'Amount',
            'Discount',
            'Final Amount',
            'Status',
            'Payment Method',
            'Date',
        ])
        
        # Data rows
        for payment in transactions:
            writer.writerow([
                payment.transaction_id,
                payment.user.username,
                payment.plan.name if payment.plan else 'N/A',
                f"₹{payment.amount}",
                f"₹{payment.discount_amount}",
                f"₹{payment.final_amount}",
                payment.get_status_display(),
                payment.payment_method,
                payment.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            ])
        
        output.seek(0)
        return output.getvalue()

    @staticmethod
    def export_to_csv_response(transactions, period='all', filename_suffix=''):
        """Generate CSV HTTP response for download"""
        csv_content = TransactionManager.export_to_csv(transactions, period)
        
        filename = f'transactions_{period}_{filename_suffix}_{timezone.now().strftime("%Y%m%d")}.csv'
        
        response = HttpResponse(csv_content, content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    @staticmethod
    def get_period_display(period):
        """Get human-readable period name"""
        period_names = {
            'week': 'Last 7 Days (Weekly)',
            'month': 'Last 30 Days (Monthly)',
            'year': 'Last 365 Days (Yearly)',
            'all': 'All Time',
        }
        return period_names.get(period, period)


def get_transaction_context(user=None, admin=False):
    """Get context data for transaction views"""
    
    if admin:
        all_transactions = Payment.objects.all().select_related('user', 'plan', 'coupon').order_by('-created_at')
    else:
        if not user:
            return None
        all_transactions = Payment.objects.filter(user=user).select_related('plan', 'coupon').order_by('-created_at')
    
    # Get period-wise data
    periods = ['week', 'month', 'year', 'all']
    period_data = {}
    
    for period in periods:
        filtered = TransactionManager.filter_transactions(all_transactions, period)
        period_data[period] = {
            'transactions': filtered,
            'stats': TransactionManager.get_transaction_stats(filtered),
            'display_name': TransactionManager.get_period_display(period),
        }
    
    return {
        'all_transactions': all_transactions,
        'period_data': period_data,
        'periods': periods,
    }
