from django.conf.urls import url, include
from . import views

app_name = 'shop'
urlpatterns = [
    url(r'^$', views.home_view, name='home_url'),
    url(r'^inverter/$', views.inverter_view, name='inverter_url'),
    url(r'^success/$', views.success, name='success_url'),
    url(r'^failure/$', views.failure, name='failure_url'),
    url(r'^inverter/(?P<company>.+)/(?P<model>.+)/$', views.inverter_product_view, name='inverter_product_url'),
    url(r'^order/inverter/(?P<company>.+)/(?P<model>.+)/$', views.inverter_order_view, name='inverter_order_url'),
    url(r'^place_order/inverter/$', views.inverter_place_order_view, name='inverter_place_order_url'),
    url(r'^all_orders/inverter/$', views.inverter_all_orders_view, name='inverter_all_orders_url'),
    url(r'^dealers/inverter/$', views.inverter_dealers_view, name='inverter_dealers_url'),
    url(r'^add_dealer/inverter/$', views.inverter_add_dealer_view, name='inverter_add_dealer_url'),
    url(r'^add_company/inverter/$', views.inverter_add_company_view, name='inverter_add_company_url'),
    url(r'^add_product/inverter/$', views.inverter_add_product_view, name='inverter_add_product_url'),
    url(r'^delete_product/inverter/(?P<company>.+)/(?P<model>.+)/$', views.inverter_delete_product_view, name='inverter_delete_product_url'),
    url(r'^delete_company/inverter/(?P<company>.+)/$', views.inverter_delete_company_view, name='inverter_delete_company_url'),
    url(r'^change_price/inverter/(?P<company>.+)/(?P<model>.+)/$', views.inverter_change_price_view, name='inverter_change_price_url'),
    url(r'^change_warranty/inverter/(?P<company>.+)/(?P<model>.+)/$', views.inverter_change_warranty_view, name='inverter_change_warranty_url'),
    url(r'^change_weight/inverter/(?P<company>.+)/(?P<model>.+)/$', views.inverter_change_weight_view, name='inverter_change_weight_url'),
    url(r'^change_quantity/inverter/(?P<company>.+)/(?P<model>.+)/$', views.inverter_change_quantity_view, name='inverter_change_quantity_url'),
    url(r'^change_recharge_time/inverter/(?P<company>.+)/(?P<model>.+)/$', views.inverter_change_recharge_time_view, name='inverter_change_recharge_time_url'),
    url(r'^change_description/inverter/(?P<company>.+)/(?P<model>.+)/$', views.inverter_change_description_view, name='inverter_change_description_url'),
    url(r'^change_photo/inverter/(?P<company>.+)/(?P<model>.+)/$', views.inverter_change_photo_view, name='inverter_change_photo_url'),
    url(r'^change_company_photo/inverter/(?P<company>.+)/$', views.inverter_change_company_photo_view, name='inverter_change_company_photo_url'),
    url(r'^change_order_status/inverter/(?P<order_id>.+)/$', views.inverter_change_order_status_view, name='inverter_change_order_status_url'),
]
