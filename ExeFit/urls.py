from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static
from . import views


urlpatterns = [
    path('register/', register_user, name='register'),
    path('', home, name='home'),
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),
    path('dashboard/', dashboard, name='dashboard'),
    path('membership/', membership, name='membership'),
    path('activities/', activity_list, name='activity_list'),
    path('book/<uuid:activity_id>/', book_activity, name='book_activity'),
    path('cancel-booking/<uuid:booking_id>/', cancel_booking, name='cancel_booking'),
    path('checkin/', checkin, name='checkin'),
    path('send_tokens/', send_tokens, name='send_tokens'),
    path('rewards/', view_rewards, name='view_rewards'),
]

# if settings.DEBUG:
#     urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)