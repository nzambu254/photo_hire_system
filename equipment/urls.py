from django.urls import path
from . import views

urlpatterns = [
    path('', views.equipment_list, name='equipment_list'),
    path('<int:pk>/', views.equipment_detail, name='equipment_detail'),
    path('add/', views.equipment_create, name='equipment_create'),
    path('<int:pk>/edit/', views.equipment_edit, name='equipment_edit'),
    path('<int:pk>/delete/', views.equipment_delete, name='equipment_delete'),
    path('manage/', views.equipment_manage, name='equipment_manage'),
    path('categories/', views.category_manage, name='category_manage'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),
]
