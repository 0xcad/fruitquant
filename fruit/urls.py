from django.urls import path, register_converter

from . import views, converters
register_converter(converters.DateConverter, 'date')

app_name = 'fruit'
urlpatterns = [
    path('', views.daily_report, name='index'),
    path('report/<date:date>', views.daily_report, name='report'),
    path('commodity/', views.commodity, name='list_commodities'),
    path('commodity/<slug:fruit_slug>', views.commodity, name='commodity'),
]
