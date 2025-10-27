# businesses/views.py  
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Business, BusinessItem, Booking
from businesses.utils import track_event  # ADD THIS LINE

def business_website_view(request, business_slug):
    """Serve dynamic business websites"""
    business = get_object_or_404(Business, slug=business_slug, is_active=True)
    
    # ADD THIS LINE - Track the visit
    track_event(business, 'visit', request)
    
    # Get items based on business type
    items = business.items.filter(is_active=True).order_by('display_order', 'name')
    
    # Select appropriate template based on business type
    template_map = {
        'menu': 'businesses/menu_site.html',
        #'salon': 'businesses/salon_site.html', 
        'shop': 'businesses/shop_site.html',
        #'service': 'businesses/service_site.html',
        'booking': 'businesses/booking_site.html',
        
    }
    
    template = template_map.get(business.business_type, 'businesses/default_site.html')
    
    context = {
        'business': business,
        'items': items,
        'menu_items': items.filter(item_type='menu_item'),
        'products': items.filter(item_type='product'), 
        'services': items.filter(item_type='service'),
    }
    
    return render(request, template, context)

def create_booking(request, business_slug):
    """Handle booking creation"""
    if request.method == 'POST':
        business = get_object_or_404(Business, slug=business_slug)
        
        booking_type_map = {
            'service': 'appointment', 
            'restaurant': 'reservation',
            'shop': 'order'
        }
        
        booking = Booking.objects.create(
            business=business,
            booking_type=booking_type_map[business.business_type],
            customer_name=request.POST['customer_name'],
            customer_phone=request.POST['customer_phone'],
            customer_email=request.POST.get('customer_email', ''),
            booking_date=request.POST['booking_date'],
            booking_time=request.POST.get('booking_time'),
            party_size=request.POST.get('party_size'),
            notes=request.POST.get('notes', '')
        )
        
        # ADD THIS - Track the booking
        track_event(business, 'booking', request, {
            'booking_id': booking.id,
            'booking_type': booking.booking_type
        })
        
        if 'selected_items' in request.POST:
            item_ids = request.POST.getlist('selected_items')
            booking.selected_items.set(item_ids)
            total = sum(item.price for item in booking.selected_items.all())
            booking.total_amount = total
            booking.save()

            # Trigger Telegram notification
        # from telegram_bot.utils import send_booking_notification
        # send_booking_notification(booking)
        
        # return JsonResponse({'success': True, 'booking_id': booking.id})
        
        return JsonResponse({'success': True, 'booking_id': booking.id})
    
    return JsonResponse({'error': 'Invalid request'})



# def public_business_view(request, slug):
#     """Public view of business page - tracks visits"""
#     from businesses.utils import track_event
    
#     business = get_object_or_404(Business, slug=slug, is_active=True)
    
#     # Track the visit
#     track_event(business, 'visit', request)
    
#     # For now, just show a simple page
#     return render(request, 'businesses/public.html', {
#         'business': business
#     })