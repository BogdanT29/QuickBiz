# businesses/utils.py
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum


def get_client_ip(request):
    """Get the real IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]  # Take first IP if multiple
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip  # Just return the IP string, not HttpResponse

def track_event(business, event_type, request=None, metadata=None):
    """
    Track an analytics event
    
    Usage:
        track_event(business, 'qr_scan', request)
        track_event(business, 'menu_view', request, {'item_id': 123})
    """
    from businesses.models import AnalyticsEvent  # Import here to avoid circular imports
    
    # Get session and IP info if request is provided
    session_id = None
    ip_address = None
    user_agent = ''
    
    if request:
        session_id = request.session.session_key
        ip_address = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
    
    # Create the event
    event = AnalyticsEvent.objects.create(
        business=business,
        event_type=event_type,
        session_id=session_id,
        ip_address=ip_address,
        user_agent=user_agent,
        metadata=metadata or {}
    )
    
    # Update daily statistics
    update_daily_stats(business, event_type)
    
    return event

def update_daily_stats(business, event_type=None):
    """Update today's daily statistics"""
    from businesses.models import DailyStatistics
    
    today = timezone.now().date()
    
    # Get or create today's stats record
    daily_stat, created = DailyStatistics.objects.get_or_create(
        business=business,
        date=today
    )

    if event_type == 'visit':
        daily_stat.visits += 1
    elif event_type == 'qr_scan':
        daily_stat.qr_scans += 1
    elif event_type == 'menu_view':
        daily_stat.menu_views += 1
    elif event_type == 'order':
        daily_stat.orders += 1
    elif event_type == 'booking':
        daily_stat.bookings += 1
    
    daily_stat.save()
    return daily_stat

def calculate_period_stats(business, days=7):
    """
    Calculate statistics for the last N days
    
    Args:
        business: Business instance
        days: Number of days to look back (default 7)
    
    Returns:
        dict with aggregated statistics
    """
    from businesses.models import DailyStatistics
    
    today = timezone.now().date()
    start_date = today - timedelta(days=days)
    
    # Get daily stats for this period
    daily_stats = DailyStatistics.objects.filter(
        business=business,
        date__gte=start_date,
        date__lte=today
    )
    
    stats = daily_stats.aggregate(
        # Write your aggregate fields here
        visits=Sum('visits'),
        qr_scans=Sum('qr_scans'),
        menu_views=Sum('menu_views'),
        orders=Sum('orders'),
        bookings=Sum('bookings'),
        revenue=Sum('revenue'),

    )
    
    # Replace None with 0 for all fields
    for key in stats:
        if stats[key] is None:
            stats[key] = 0
    
    return stats

def calculate_comparison_stats(business, days=7):
    """
    Calculate stats with comparison to previous period
    
    Returns:
        dict with current, previous, change_percent, and is_positive
    """
    from businesses.models import DailyStatistics
    
    today = timezone.now().date()
    
    # Current period
    current_start = today - timedelta(days=days)
    current_stats = DailyStatistics.objects.filter(
        business=business,
        date__gte=current_start,
        date__lte=today
    ).aggregate(
        visits=Sum('visits'),
        qr_scans=Sum('qr_scans'),
        menu_views=Sum('menu_views'),
        orders=Sum('orders'),
        revenue=Sum('revenue'),
    )
    
    # Previous period (same length, just before current period)
    previous_start = current_start - timedelta(days=days)
    previous_end = current_start - timedelta(days=1)
    
    # Your turn: Write the query for previous_stats
    # It should be similar to current_stats but with different date range
    # Use date__gte=previous_start and date__lte=previous_end
    previous_stats = DailyStatistics.objects.filter(
        business=business,
        date__gte=previous_start,
        date__lte=previous_end
        # Write your filter here
    ).aggregate(
        visits=Sum('visits'),
        qr_scans=Sum('qr_scans'),
        menu_views=Sum('menu_views'),
        orders=Sum('orders'),
        revenue=Sum('revenue'),
        # Write your aggregate here (same as current_stats)
    )
    
    # Calculate changes
    changes = {}
    for key in current_stats:
        current = current_stats[key] or 0
        previous = previous_stats[key] or 0
        
        # Your turn: Calculate the percentage change
        # Formula: ((current - previous) / previous) * 100
        # Handle the case when previous is 0
        if previous > 0:
            change_percent = ((current - previous) / previous) * 100
        else:
            change_percent = 100 if current > 0 else 0
        
        changes[key] = {
            'current': current,
            'previous': previous,
            'change_percent': round(change_percent, 1),
            'is_positive': change_percent >= 0
        }
    
    return changes