from django.contrib import admin
from .models import Business, BusinessItem, Booking, Statistics, DailyStatistics, AnalyticsEvent

admin.site.register(Business)
admin.site.register(BusinessItem)
admin.site.register(Booking)
admin.site.register(Statistics)
admin.site.register(DailyStatistics)
admin.site.register(AnalyticsEvent)