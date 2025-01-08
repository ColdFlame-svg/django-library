from django.urls import path
from . import views
from .views import logout_view
from django.contrib.auth import views as auth_views

urlpatterns = [
# HOMEPAGE  
    path('', views.landing_page, name='landing_page'),
    path('forgotpassword/', views.forgot_password, name='forgot_password'),
    path('reset-password/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
    path('accounts/login/', views.login_view, name='login'),  # Change to '/accounts/login/'
    path('createaccount/', views.create_account, name='create_account'),
#LOGOUT
    path('logout/', logout_view, name='logout_view'),

#ADMIN

    #staff
    path('addstaff/', views.add_staff, name='add_staff'),
    path('staff/<int:staff_id>/', views.staff_detail, name='view_details'),
    path('new_staff/', views.new_staff, name='new_staff'),
    path('remove-staff/<int:staff_id>/', views.remove_staff, name='remove_staff'),
    
    #book
    path('shelf/', views.admin_shelf, name='admin_shelf'),
    path('shelf/<int:book_id>/', views.book_detail, name='view_book_details'),
    path('add-book/', views.add_book, name='add_book'),
    path('edit-book/<int:book_id>/', views.edit_book, name='edit_book'),
    path('remove_book/<int:book_id>/', views.remove_book, name='remove_book'),

    #student
    path('users/', views.admin_users, name='admin_users'),
    path('user/<int:id>/', views.account_detail, name='view_user_details'),
    path('user/remove/<int:id>/', views.remove_user, name='remove_user'),
    #fines
    path('fines', views.fines_view, name='fines'),
    path('fines/<int:fine_id>/', views.fines_detail_view, name='fines_detail'),
    path('pay/<int:id>/', views.pay_fine, name='pay_fine'), 
    #password
    path('change-password/', views.password_change, name='adchange_password'),
    




#STAFF

    path('books/logout/', views.logout_view, name='staff_logout'),
#shelf
    path('books/', views.staff_books_view, name='staff_books'),
    path('book/<int:book_id>/', views.staff_book_detail, name='staff_book_detail'),
#accounts
    path('account/', views.user_account, name='user_account'),
    path('account/<int:user_id>/', views.view_user_account, name='view_user_account'),
#transactions
    
    path('transaction/create/', views.create_transaction, name='create_transaction'),
    path('transaction/remove/<str:transaction_id>/', views.remove_transaction, name='remove_transaction'),
#changepassword
    path('staff/password/change/', views.staff_password_change, name='staff_password_change'),
#download report
    path('download_report/', views.download_report, name='download_report'),



#STUDENT

#dashboard
    path('dashboard/', views.student_dashboard, name='student_dashboard'),
    path('student/logout/', views.logout_view, name='student_logout'),
#books
    path('item/', views.student_books, name='student_shelf'),
    path('item/<int:pk>/', views.shelf_detail, name='student_shelf_detail'),
#change password
    path('password/', views.change_password, name='change_password'),

#forgot password
 path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),





]
