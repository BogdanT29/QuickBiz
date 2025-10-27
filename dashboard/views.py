from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from businesses.models import Business, BusinessItem, Statistics
from businesses.utils import (
    calculate_comparison_stats,
    calculate_period_stats
)
@login_required
def setup_business(request):
    """Handle the business setup quiz"""
    if request.method == 'POST':
        # Since owner is ForeignKey, we need to handle differently
        # Get existing incomplete business or create new one
        business = Business.objects.filter(
            owner=request.user, 
            is_setup_complete=False
        ).first()
        
        if business:
            # Update existing incomplete business
            business.business_type = request.POST.get('business_type')
            business.name = request.POST.get('business_name')
            business.description = request.POST.get('business_description', '')
            business.address = request.POST.get('business_address', '')
            business.phone = request.POST.get('business_phone')
            business.email = request.POST.get('business_email', '')
            business.telegram_username = request.POST.get('telegram_username', '')
            business.is_setup_complete = True
            business.save()
        else:
            # Create new business
            business = Business.objects.create(
                owner=request.user,
                business_type=request.POST.get('business_type'),
                name=request.POST.get('business_name'),
                description=request.POST.get('business_description', ''),
                address=request.POST.get('business_address', ''),
                phone=request.POST.get('business_phone'),
                email=request.POST.get('business_email', ''),
                telegram_username=request.POST.get('telegram_username', ''),
                is_setup_complete=True,
            )
        
        return JsonResponse({'success': True, 'redirect': '/dashboard/'})
    
    return render(request, 'dashboard/quiz.html')

@login_required
def dashboard_view(request):
    
    business = get_object_or_404(Business, owner=request.user)
    
    # Get or create statistics
    stats, created = Statistics.objects.get_or_create(business=business)

     # Get comparison stats for the week
    comparison_stats = calculate_comparison_stats(business, days=7)

    # Get today's stats
    today_stats = calculate_period_stats(business, days=1)
    
    # Get week stats
    week_stats = calculate_period_stats(business, days=7)
    
    # Get navigation based on business type
    navigation = get_navigation_config(business.business_type)
    
    # Get stats data
    stats_data = get_stats_config(business.business_type, stats, comparison_stats)
    
    # Get recent items
    recent_items = BusinessItem.objects.filter(
        business=business,
        is_active=True
    ).order_by('-created_at')[:5]
    
    # Get quick actions
    quick_actions = get_quick_actions(business.business_type)
    
    # Get primary action text
    primary_action_text = get_primary_action_text(business.business_type)
    
    # Get main content title
    main_content_title = get_main_content_title(business.business_type)
    
    context = {
        'business': business,
        'navigation': navigation,
        'stats': stats_data,
        'recent_items': recent_items,
        'quick_actions': quick_actions,
        'primary_action_text': primary_action_text,
        'main_content_title': main_content_title,
        'comparison_stats': comparison_stats,  # ADD THIS LINE
        'today_stats': today_stats,            # ADD THIS LINE
        'week_stats': week_stats,              # ADD THIS LINE
    }
    
    return render(request, 'dashboard/dashboard.html', context)



def get_navigation_config(business_type):
    configs = {
        'menu': [
            {
                'section': 'Основне',
                'items': [
                    {'name': 'Dashboard', 'icon': 'fas fa-chart-line', 'href': '/dashboard/', 'active': True},
                    {'name': 'Меню', 'icon': 'fas fa-utensils', 'href': '/items/'},
                    {'name': 'Категорії', 'icon': 'fas fa-tags', 'href': '/categories/'},
                ]
            },
            {
                'section': 'Налаштування',
                'items': [
                    {'name': 'QR-коди', 'icon': 'fas fa-qrcode', 'href': '/qr/'},
                    {'name': 'Дизайн', 'icon': 'fas fa-palette', 'href': '/design/'},
                    {'name': 'Налаштування', 'icon': 'fas fa-cog', 'href': '/settings/'},
                ]
            }
        ],
        'shop': [
            {
                'section': 'Основне',
                'items': [
                    {'name': 'Dashboard', 'icon': 'fas fa-chart-line', 'href': '/dashboard/', 'active': True},
                    {'name': 'Товари', 'icon': 'fas fa-box', 'href': '/items/'},
                    {'name': 'Замовлення', 'icon': 'fas fa-shopping-cart', 'href': '/orders/'},
                ]
            }
        ],
        'booking': [
            {
                'section': 'Основне',
                'items': [
                    {'name': 'Dashboard', 'icon': 'fas fa-chart-line', 'href': '/dashboard/', 'active': True},
                    {'name': 'Календар', 'icon': 'fas fa-calendar-alt', 'href': '/calendar/'},
                    {'name': 'Послуги', 'icon': 'fas fa-concierge-bell', 'href': '/items/'},
                ]
            }
        ]
    }
    return configs.get(business_type, configs['menu'])


def get_stats_config(business_type, stats, comparison_stats):
    if business_type == 'menu':
        visits_data = comparison_stats.get('visits', {})
        menu_views_data = comparison_stats.get('menu_views', {})
        qr_scans_data = comparison_stats.get('qr_scans', {})
    
        return [
            {
                'title': 'Загальні відвідування',
                'value': visits_data.get('current', 0),
                'change': f"{visits_data.get('change_percent', 0):+.0f}%",
                'positive': visits_data.get('is_positive', True),
                'icon': 'fas fa-users',
                'color': '#3b82f6'
            },
            {
                'title': 'Переглядів меню',
                'value': menu_views_data.get('current', 0),
                'change': f"{menu_views_data.get('change_percent', 0):+.0f}%",
                'positive': menu_views_data.get('is_positive', True),
                'icon': 'fas fa-eye',
                'color': '#22c55e'
            },
            {
                'title': 'QR-сканування',
                'value': qr_scans_data.get('current', 0),
                'change': f"{qr_scans_data.get('change_percent', 0):+.0f}%",
                'positive': qr_scans_data.get('is_positive', True),
                'icon': 'fas fa-qrcode',
                'color': '#f59e0b'
            },
        ]
    elif business_type == 'shop':
        # Get real comparison data
        orders_data = comparison_stats.get('orders', {})
        revenue_data = comparison_stats.get('revenue', {})
        visits_data = comparison_stats.get('visits', {})
        
        return [
            {
                'title': 'Загальний дохід', 
                'value': f'₴{revenue_data.get("current", 0):,.0f}',
                'change': f"{revenue_data.get('change_percent', 0):+.0f}%",
                'positive': revenue_data.get('is_positive', True),
                'icon': 'fas fa-hryvnia-sign', 
                'color': '#22c55e'
            },
            {
                'title': 'Замовлення', 
                'value': orders_data.get('current', 0),
                'change': f"{orders_data.get('change_percent', 0):+.0f}%",
                'positive': orders_data.get('is_positive', True),
                'icon': 'fas fa-shopping-cart', 
                'color': '#3b82f6'
            },
            {
                'title': 'Відвідування', 
                'value': visits_data.get('current', 0),
                'change': f"{visits_data.get('change_percent', 0):+.0f}%",
                'positive': visits_data.get('is_positive', True),
                'icon': 'fas fa-users', 
                'color': '#f59e0b'
            },
        ]
    elif business_type == 'booking':
    # Get real comparison data
        visits_data = comparison_stats.get('visits', {})
        bookings_data = comparison_stats.get('bookings', {})
        
        return [
            {
                'title': 'Відвідування тижня',
                'value': visits_data.get('current', 0),
                'change': f"{visits_data.get('change_percent', 0):+.0f}%",
                'positive': visits_data.get('is_positive', True),
                'icon': 'fas fa-chart-line',
                'color': '#3b82f6'
            },
            {
                'title': 'Записи цього тижня',
                'value': bookings_data.get('current', 0),
                'change': f"{bookings_data.get('change_percent', 0):+.0f}%",
                'positive': bookings_data.get('is_positive', True),
                'icon': 'fas fa-calendar-week',
                'color': '#22c55e'
            },
            {
                'title': 'Записи сьогодні',
                'value': stats.appointments_today,
                'change': '+0%',
                'positive': True,
                'icon': 'fas fa-calendar-day',
                'color': '#f59e0b'
            },
        ]
    return []


def get_quick_actions(business_type):
    actions = {
        'menu': [
            {'title': 'Додати страву', 'description': 'Додайте нову страву до меню', 'icon': 'fas fa-plus', 'href': '/items/add/'},
            {'title': 'Створити категорію', 'description': 'Організуйте страви за категоріями', 'icon': 'fas fa-folder-plus', 'href': '/categories/add/'},
            {'title': 'Згенерувати QR-код', 'description': 'Створіть QR-код для столиків', 'icon': 'fas fa-qrcode', 'href': '/qr/'},
        ],
        'shop': [
            {'title': 'Додати товар', 'description': 'Додайте новий товар до каталогу', 'icon': 'fas fa-plus', 'href': '/items/add/'},
            {'title': 'Обробити замовлення', 'description': 'Переглянути нові замовлення', 'icon': 'fas fa-clipboard-check', 'href': '/orders/'},
        ],
        'booking': [
            {'title': 'Додати послугу', 'description': 'Створіть нову послугу для запису', 'icon': 'fas fa-plus', 'href': '/items/add/'},
            {'title': 'Переглянути календар', 'description': 'Керуйте записами та розкладом', 'icon': 'fas fa-calendar-alt', 'href': '/calendar/'},
        ]
    }
    return actions.get(business_type, actions['menu'])


def get_primary_action_text(business_type):
    texts = {
        'menu': 'Додати страву',
        'shop': 'Додати товар',
        'booking': 'Додати послугу',
    }
    return texts.get(business_type, 'Додати')


def get_main_content_title(business_type):
    titles = {
        'menu': 'Популярні страви',
        'shop': 'Останні замовлення',
        'booking': 'Найближчі записи',
    }
    return titles.get(business_type, 'Останні дані')

@login_required
def items_list(request):
    return render(request, 'items_list.html')

@login_required  
def add_item(request):
    return render(request, 'add_item.html')