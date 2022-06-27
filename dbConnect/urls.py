from django.urls import path
from. import views

urlpatterns = [
    path('test_web', views.test_web),
    path('print_insta_ID', views.print_insta_ID),
    path('add_user', views.add_user),
    path('check_id', views.check_id),
    path('check_email', views.check_email),
    path('find_id', views.find_id),
    path('find_pw', views.find_pw),
    path('app_login', views.app_login),
    path('find_insta_id', views.find_insta_id),
    path('saved_instaID', views.saved_instaID),
    path('delete_instaID', views.delete_instaID),
    path('show_saved_Image', views.show_saved_Image),
    path('save_selected_image', views.save_selected_image),
    path('delete_selected_image', views.delete_selected_image),

]
