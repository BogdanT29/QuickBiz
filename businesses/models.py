# businesses/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.utils import timezone
from datetime import timedelta

class Business(models.Model):
    """Main business model - handles all business types"""
    
    BUSINESS_TYPES = [
        ('menu', 'Онлайн меню'),
        ('shop', 'Інтернет-магазин'), 
        ('booking', 'Система запису'),
    ]
    
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='businesses')
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    business_type = models.CharField(max_length=20, choices=BUSINESS_TYPES)
    description = models.TextField(blank=True)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    telegram_username = models.CharField(max_length=50, blank=True)
    is_setup_complete = models.BooleanField(default=False)
    primary_color = models.CharField(max_length=7, default='#007bff')
    logo = models.ImageField(upload_to='business_logos/', blank=True)
    cover_image = models.ImageField(upload_to='business_covers/', blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Business.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name


class BusinessItem(models.Model):
    """Universal model for menu items, products, services"""
    
    ITEM_TYPES = [
        ('menu_item', 'Menu Item'),
        ('product', 'Product'),
        ('service', 'Service'),
    ]
    
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='items')
    item_type = models.CharField(max_length=20, choices=ITEM_TYPES)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='business_items/', blank=True)
    stock_quantity = models.PositiveIntegerField(default=0, blank=True, null=True)
    sku = models.CharField(max_length=50, blank=True)
    duration_minutes = models.PositiveIntegerField(blank=True, null=True)
    category = models.CharField(max_length=100, blank=True)
    is_vegetarian = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['display_order', 'name']
    
    def __str__(self):
        return f"{self.business.name} - {self.name}"


class Booking(models.Model):
    """Universal booking model"""
    
    BOOKING_TYPES = [
        ('appointment', 'Appointment'),
        ('reservation', 'Table Reservation'),
        ('order', 'Product Order'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'), 
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='bookings')
    booking_type = models.CharField(max_length=20, choices=BOOKING_TYPES)
    customer_name = models.CharField(max_length=100)
    customer_phone = models.CharField(max_length=20)
    customer_email = models.EmailField(blank=True, null=True)
    booking_date = models.DateField()
    booking_time = models.TimeField(blank=True, null=True)
    selected_items = models.ManyToManyField(BusinessItem, blank=True)
    party_size = models.PositiveIntegerField(blank=True, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.business.name} - {self.customer_name} ({self.booking_date})"


# NEW: Daily statistics tracking model
class DailyStatistics(models.Model):
    """Track daily statistics for detailed analytics"""
    
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='daily_stats')
    date = models.DateField(default=timezone.now)
    
    # Traffic metrics
    visits = models.PositiveIntegerField(default=0)
    unique_visitors = models.PositiveIntegerField(default=0)
    qr_scans = models.PositiveIntegerField(default=0)
    menu_views = models.PositiveIntegerField(default=0)
    
    # Business metrics
    orders = models.PositiveIntegerField(default=0)
    bookings = models.PositiveIntegerField(default=0)
    revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Customer metrics
    new_customers = models.PositiveIntegerField(default=0)
    returning_customers = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['business', 'date']
        ordering = ['-date']
        verbose_name_plural = 'Daily statistics'
    
    def __str__(self):
        return f"{self.business.name} - {self.date}"


# NEW: Event tracking for detailed analytics
class AnalyticsEvent(models.Model):
    """Track individual events for analytics"""
    
    EVENT_TYPES = [
        ('visit', 'Page Visit'),
        ('qr_scan', 'QR Code Scan'),
        ('menu_view', 'Menu View'),
        ('item_view', 'Item View'),
        ('booking', 'Booking Created'),
        ('order', 'Order Placed'),
    ]
    
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='events')
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    
    # Session tracking
    session_id = models.CharField(max_length=100, blank=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True)
    
    # Additional data
    metadata = models.JSONField(default=dict, blank=True)  # For storing extra info
    
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['business', 'event_type', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.business.name} - {self.event_type} - {self.timestamp}"


class Statistics(models.Model):
    """Aggregated statistics for the business"""
    
    business = models.OneToOneField(Business, on_delete=models.CASCADE, related_name='statistics')
    
    # All-time totals
    total_visits = models.PositiveIntegerField(default=0)
    total_bookings = models.PositiveIntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_customers = models.PositiveIntegerField(default=0)
    menu_views = models.PositiveIntegerField(default=0)
    qr_scans = models.PositiveIntegerField(default=0)
    total_orders = models.PositiveIntegerField(default=0)
    
    # Previous period for comparison (auto-updated)
    prev_total_visits = models.PositiveIntegerField(default=0)
    prev_menu_views = models.PositiveIntegerField(default=0)
    prev_qr_scans = models.PositiveIntegerField(default=0)
    prev_total_orders = models.PositiveIntegerField(default=0)
    prev_total_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Shop specific
    total_products_sold = models.PositiveIntegerField(default=0)
    average_order_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Booking specific
    appointments_today = models.PositiveIntegerField(default=0)
    appointments_week = models.PositiveIntegerField(default=0)
    
    last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Statistics for {self.business.name}"
    
    # Helper methods for time-based queries
    def get_stats_for_period(self, days=7):
        """Get statistics for the last N days"""
        start_date = timezone.now().date() - timedelta(days=days)
        daily_stats = self.business.daily_stats.filter(date__gte=start_date)
        
        return {
            'visits': sum(s.visits for s in daily_stats),
            'qr_scans': sum(s.qr_scans for s in daily_stats),
            'menu_views': sum(s.menu_views for s in daily_stats),
            'orders': sum(s.orders for s in daily_stats),
            'bookings': sum(s.bookings for s in daily_stats),
            'revenue': sum(s.revenue for s in daily_stats),
        }
    
    def get_today_stats(self):
        """Get today's statistics"""
        return self.get_stats_for_period(days=1)
    
    def get_week_stats(self):
        """Get this week's statistics"""
        return self.get_stats_for_period(days=7)
    
    def get_month_stats(self):
        """Get this month's statistics"""
        return self.get_stats_for_period(days=30)