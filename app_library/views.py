from django.shortcuts import render, redirect , get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, authenticate, update_session_auth_hash, logout
from django.contrib.auth.decorators import login_required 
from django.views.decorators.cache import never_cache
from django.utils import timezone
from django.db import transaction
from django.http import HttpResponseRedirect    
from django.urls import reverse
from django.db.models import Q
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie

from .forms import (
    CreateAccountForm, 
    AddStaffForm, 
    BookForm, 
    PasswordChangeForm, 
    TransactionForm,
    StaffPasswordChangeForm
)
from .models import Staff, RemovedStaff, Book, User, Transaction, RemovedBook, Fine, Admin
import csv
from django.http import HttpResponse
from .models import Transaction
from io import StringIO
from django.core.mail import EmailMessage
from django.conf import settings



# Create your views here.


#LOGIN

def landing_page(request):
    # Render the landing page
    return render(request, 'login/landing.html')

#@csrf_protect
#@never_cache
def login_view(request):
    # Check if the user is already authenticated
    if request.user.is_authenticated:
        return redirect('student_dashboard')  # or wherever the authenticated user should go

    # If session has expired, show an expired message
    if 'session_expired' in request.GET:
        messages.error(request, "Your session has expired. Please log in again.")

    if request.method == "POST":
        username = request.POST.get('uname')  # Username
        password = request.POST.get('upass')  # Password

        # Authenticate the user
        user = authenticate(request, username=username, password=password)

        if user:
            # Log in the user
            login(request, user)

            # Store user details in session
            request.session['user_id'] = user.id
            request.session['firstname'] = user.first_name
            request.session['surname'] = user.last_name
            request.session['role'] = (
                'admin' if user.is_admin else
                'superuser' if user.is_superuser else
                'staff' if user.is_staff else
                'student'
            )

            # Redirect based on the 'next' URL parameter
            next_url = request.GET.get('next', None)
            if next_url:
                return redirect(next_url)  # Redirect to the requested page
            else:
                # Redirect based on the user role if no 'next' parameter
                if user.is_admin or user.is_superuser:
                    return redirect('add_staff')
                elif user.is_staff:
                    return redirect('staff_books')
                else:
                    return redirect('student_dashboard')

        else:
            messages.error(request, "Invalid username or password. Please try again.")
            return redirect('login')

    # Render the login page if not a POST request
    return render(request, 'login/landing.html')

from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.core.mail import send_mail


def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get('email')
        
        # Check if the user exists with that email
        try:
            user = User.objects.get(email=email)
            
            # Generate a password reset token and uid
            uid = urlsafe_base64_encode(user.pk.encode('utf-8'))
            token = default_token_generator.make_token(user)

            # Build the reset URL
            reset_url = f"{get_current_site(request).domain}/reset-password/{uid}/{token}/"

            # Create the email content
            subject = 'Password Reset Request'
            message = render_to_string('login/reset_email_template.html', {
                'user': user,
                'reset_url': reset_url,
            })
            
            # Send the email
            send_mail(subject, message, 'no-reply@mywebsite.com', [email])

            # Success message
            messages.success(request, "A password reset link has been sent to your email.")
            return redirect('forgot_password')

        except User.DoesNotExist:
            messages.error(request, "No user found with this email.")
            return redirect('forgot_password')
        
    return render(request, 'login/forgotpassword.html')


from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth import get_user_model  

def password_reset_confirm(request, uidb64, token):
    try:
        # Decode user ID from URL
        uid = urlsafe_base64_decode(uidb64).decode('utf-8')
        user = get_user_model().objects.get(pk=uid)

        # Check if the token is valid
        if default_token_generator.check_token(user, token):
            if request.method == 'POST':
                form = SetPasswordForm(user, request.POST)
                if form.is_valid():
                    form.save()  # Save the new password
                    messages.success(request, "Your password has been reset successfully.")
                    return redirect('login')
            else:
                form = SetPasswordForm(user)
            return render(request, 'login/password_reset_form.html', {'form': form})

        else:
            messages.error(request, "The link is invalid or expired.")
            return redirect('login')

    except Exception as e:
        messages.error(request, f"Error: {str(e)}")
        return redirect('login')

def create_account(request):
    if request.method == 'POST':
        form = CreateAccountForm(request.POST)
        if form.is_valid():
            # Save the new user account
            user = form.save(commit=False)
            user.password = form.cleaned_data['password']  # You should hash this password before saving
            user.save()
            messages.success(request, "Account created successfully.")
            return redirect('landing_page')  # Redirect to the login page after successful account creation
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CreateAccountForm()

    return render(request, 'login/createaccount.html', {'form': form})


#ADMIN

def create_admin(student_id, password, **extra_fields):
    # Create a user with admin privileges
    user = User.objects.create_user(student_id=student_id, password=password, **extra_fields)
    user.is_admin = True
    user.save()

    # Link the user to the Admin table
    Admin.objects.create(user=user)
    return user
#staff
#@login_required
#@never_cache
def add_staff(request):
    search_query = request.GET.get('search', '')
    
    # Filter staff members based on search query
    if search_query:
        staff_members = Staff.objects.filter(
            staff_id__icontains=search_query
        ) | Staff.objects.filter(
            first_name__icontains=search_query
        ) | Staff.objects.filter(
            last_name__icontains=search_query
        )
    else:
        staff_members = Staff.objects.all()

    return render(request, 'admin/addstaff.html', {'staff_members': staff_members})
#@never_cache
#@login_required
def staff_detail(request, staff_id):
    # Fetch the specific staff member by staff_id
    staff = get_object_or_404(Staff, pk=staff_id)
    return render(request, 'admin/staffdetail.html', {'staff': staff})
#@never_cache
#@login_required
def new_staff(request):
    if request.method == "POST":
        form = AddStaffForm(request.POST)
        if form.is_valid():
            staff = form.save(commit=False)  # Create the Staff instance but don’t save yet

            # Create a linked User instance
            user = User.objects.create_user(
                student_id=form.cleaned_data['staff_id'],  # Use staff_id as student_id
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],  # Use the same password
                is_staff=True,  # Mark as staff
            )

            staff.user = user  # Link the Staff instance to the User
            staff.save()  # Save the Staff instance

            # Add a success message
            messages.success(request, "Staff member added successfully.")
            return redirect('add_staff')  # Redirect to the add staff page
    else:
        form = AddStaffForm()

    return render(request, 'admin/newstaff.html', {'form': form})
#@login_required
def remove_staff(request, staff_id):
    if request.method == 'POST':
        # Start an atomic transaction to ensure consistency
        with transaction.atomic():
            # Get the staff member by ID
            staff = get_object_or_404(Staff, id=staff_id)

            # Create a record in RemovedStaff with the necessary fields
            RemovedStaff.objects.create(
                staff=staff,  # Link to the Staff record via foreign key
                removed_staff_id=staff.staff_id,  # Store staff_id in removed staff record
                staff_name=f"{staff.first_name} {staff.last_name}",  # Full name of staff
                date_removed=timezone.now()  # Record the removal date and time
            )

            # Now, delete the staff member from the Staff model
            staff.delete()  # This will remove the staff record from the Staff table

        # Redirect to the staff list page or confirmation page
        return redirect('add_staff')  # Adjust this to your desired redirect

    else:
        # If the request method is not POST, redirect to the staff list page
        return redirect('add_staff')
#shelf
#@never_cache
#@login_required
def admin_shelf(request):
    search_query = request.GET.get('search', '')
    
    # Filter books based on the search query
    if search_query:
        books = Book.objects.filter(
            title__icontains=search_query
        ) | Book.objects.filter(
            author__icontains=search_query
        )
    else:
        books = Book.objects.all()

    return render(request, 'admin/shelf.html', {'books': books})

#@never_cache
#@login_required
def book_detail(request, book_id):
    # Fetch the book by its ID
    book = get_object_or_404(Book, pk=book_id)
    
    # Retrieve the latest transaction for the book where the return_date is either None (not returned) or in the future (still borrowed)
    transaction = Transaction.objects.filter(
        title=book,
        return_date__gte=timezone.now().date()  # This ensures we find books that are still borrowed and the return_date is in the future
    ).order_by('-borrow_date').first()

    # Get the borrower from the transaction, if it exists
    borrower = transaction.student_id if transaction else None
    
    # Pass the book and borrower to the template
    return render(request, 'admin/bookdetail.html', {
        'book': book,
        'borrower': borrower,
    })
#@never_cache
#@login_required
def add_book(request):
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)  # Handle the form data, including files
        if form.is_valid():
            form.save()  # Save the new book to the database
            return redirect('admin_shelf')  # Redirect to the shelf page after adding the book
    else:
        form = BookForm()  # Create an empty form for GET requests

    # Ensure the view returns a response with the rendered form
    return render(request, 'admin/addbook.html', {'form': form})
#@never_cache
#@login_required
def edit_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            form.save()  # Save the edited book
            return redirect('admin_shelf')  # Redirect to admin shelf after saving
    else:
        form = BookForm(instance=book)  # Pre-fill the form with the book's current data

    return render(request, 'admin/editbook.html', {'form': form, 'book': book})
#@never_cache
#@login_required
def remove_book(request, book_id):
    if request.method == 'POST':
        # Start an atomic transaction to ensure consistency
        with transaction.atomic():
            # Get the book by ID
            book = get_object_or_404(Book, id=book_id)

            # Create a record in RemovedBook with the relevant data
            RemovedBook.objects.create(
                
                removed_isbn=book.isbn,
                title=book.title,
                removed_book_id=book.id,  # Copy book id to removed book id
                published_date=book.published_date,
                date_removed=timezone.now()
            )

            # Delete the book from the Book model
            book.delete()

        # Redirect to the 'admin_shelf' or another confirmation page
        return redirect('admin_shelf')
    
    # If the request method is not POST, redirect back to 'admin_shelf'
    return redirect('admin_shelf')


#students
#@never_cache
#@login_required
def admin_users(request):
    search_query = request.GET.get('search', '')

    if search_query:
        users = User.objects.filter(
            student_id__icontains=search_query
        ) | User.objects.filter(
            first_name__icontains=search_query
        ) | User.objects.filter(
            middle_name__icontains=search_query
        ) | User.objects.filter(
            last_name__icontains=search_query
        ) | User.objects.filter(
            email__icontains=search_query
        )
    else:
        users = User.objects.filter(is_staff=False, is_superuser=False, is_admin = False)
    return render(request, 'admin/users.html', {'users': users})
# View to display the details of a specific user (admin/accountdetail.html)
#@never_cache
#@login_required
def account_detail(request, id):
    user = get_object_or_404(User, id=id)  # Get user by ID, or 404 if not found
    return render(request, 'admin/accountdetail.html', {'user': user})
# Remove User view (this would handle user removal logic)
#@never_cache
#@login_required
def remove_user(request, id):
    user = get_object_or_404(User, id=id)
    user.delete()  # Delete the user from the database
    return redirect('admin_users') 

#fines
#@never_cache
#@login_required
def fines_view(request):
    search_query = request.GET.get('search', '')

    if search_query:
        fines = Fine.objects.filter(
            student_id__icontains=search_query
        ) | Fine.objects.filter(
            book_title__icontains=search_query
        ) | Fine.objects.filter(
            days_overdue__icontains=search_query
        )
    else:
        fines = Fine.objects.all()
    
    return render(request, 'admin/fines.html', {'fines': fines})
#@never_cache
#@login_required
def fines_detail_view(request, fine_id):
    fine = get_object_or_404(Fine, id=fine_id)  # Get the fine by ID, or 404 if not found
    return render(request, 'admin/finesdetail.html', {'fine': fine})
#@never_cache
#@login_required
def pay_fine(request, id):
    fine = get_object_or_404(Fine, id=id)  # Get the fine by ID
    fine.delete()  # Remove the fine from the database (or mark it as paid if you prefer)
    return redirect('fines')  # Redirect to the list of fines

#change_password
#@never_cache
#@login_required
def password_change(request):

    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            # Save the new password
            form.save()

            # Add a success message
            messages.success(request, "Your password has been successfully changed.")

            return redirect('login')  # Redirect after successful form submission
    else:
        form = PasswordChangeForm(request.user)  # Pass the user to the form

    return render(request, 'admin/adpassword.html', {'form': form})






#STAFF
    
#shelf


#@login_required
#@never_cache
def staff_books_view(request):
    # Get the search query from the GET request
    search_query = request.GET.get('search', '')

    # Retrieve books based on the search query
    if search_query:
        books = Book.objects.filter(
            title__icontains=search_query
        ) | Book.objects.filter(
            author__icontains=search_query
        )
    else:
        books = Book.objects.all()  # Retrieve all available books if no search query is provided

    # Optional: Display staff-specific information
    staff_id = request.session.get('staff_id')
    staff_member = None
    if staff_id:
        staff_member = Staff.objects.filter(staff_id=staff_id).first()

    return render(request, 'staff/staffbooks.html', {'staff_member': staff_member, 'books': books})
    
#@never_cache    
#@login_required
def staff_book_detail(request, book_id):
    # Fetch the book by its ID
    book = get_object_or_404(Book, id=book_id)

    # Retrieve the latest transaction where the book is not yet returned or overdue
    transaction = Transaction.objects.filter(
        title=book,
        return_date__isnull=False  # Make sure we fetch transactions with a return date
    ).order_by('-borrow_date').first()

    # Initialize borrower and overdue_days
    borrower = None
    overdue_days = 0

    # Check if there's an active transaction
    if transaction:
        borrower = transaction.student_id  # Fetch the borrower
        # Dynamically calculate overdue days
        today = timezone.now().date()
        if transaction.return_date < today:
            overdue_days = (today - transaction.return_date).days  # Calculate overdue days

    # Pass the book, borrower, and overdue_days to the template
    return render(request, 'staff/itemdetail.html', {
        'book': book,
        'borrower': borrower,
        'overdue_days': overdue_days,
    })
#accounts
#@never_cache
#@login_required
def user_account(request):
    # Get the search query from the GET request
    search_query = request.GET.get('search', '')

    # Filter users based on the search query
    if search_query:
        accounts = User.objects.filter(
            is_staff=False, is_superuser=False
        ).filter(
            student_id__icontains=search_query
        ) | User.objects.filter(
            is_staff=False, is_superuser=False
        ).filter(
            first_name__icontains=search_query
        ) | User.objects.filter(
            is_staff=False, is_superuser=False
        ).filter(
            last_name__icontains=search_query
        )
    else:
        # If no search query is provided, fetch all users
        accounts = User.objects.filter(is_staff=False, is_superuser=False, is_admin = False)

    return render(request, 'staff/staffaccount.html', {'users': accounts})
#@never_cache
#@login_required
def view_user_account(request, user_id):
    # Fetch the specific user account or return a 404 error if not found
    user = get_object_or_404(User, id=user_id)
    
    # Fetch the transactions for this user (if any)
    transactions = Transaction.objects.filter(student_id=user)  # Adjust the relationship if needed
    
    # Render the template and pass both the user and transactions
    return render(request, 'staff/acc.html', {
        'user': user,
        'transactions': transactions
    })


#transactions
#@login_required
#@never_cache
def remove_transaction(request, transaction_id):
    # Get the transaction by string ID
    transaction = get_object_or_404(Transaction, transaction_id=transaction_id)  # Use `transaction_id` instead of `id`
    
    # Assuming that each transaction is related to a student, retrieve the user_id for redirect
    user_id = transaction.student_id.id  # Store the user ID for redirect
    
    # Delete the transaction
    transaction.delete()
    
    # Redirect to the user's account details page
  
    return redirect('view_user_account', user_id=user_id)
#@login_required
#@never_cache
def create_transaction(request):
    # If the form is submitted via POST, process the form
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            # Save the form or perform your logic here
            form.save()

            # Show a success message after the form is successfully submitted
            messages.success(request, "Transaction has been created successfully.")

            # Clear the form by creating a new instance of the form
            form = TransactionForm()

            # Re-render the page with the success message and a new empty form
            return render(request, 'staff/transacform.html', {'form': form})
    
    # If the form is not submitted (i.e., GET request), create a new form instance
    else:
        form = TransactionForm()

    # Always return an HttpResponse, either by rendering a template or a redirect
    return render(request, 'staff/transacform.html', {'form': form})

def download_report(request):
    # Get the recipient email from the form input (if available)
    recipient_email = request.POST.get('email', 'default@example.com')  # Default email if not provided
    
    # Create a StringIO object to simulate a file
    csv_file = StringIO()
    
    # Create CSV writer
    writer = csv.writer(csv_file)
    
    # Write header row
    writer.writerow(['Transaction ID', 'Student ID', 'Student Name', 'Book Title', 'Borrow Date', 'Return Date', 'Days Overdue', 'Fine Amount'])
    
    # Write data rows
    for transaction in Transaction.objects.all():
        fine_amount = transaction.days_overdue * 5.0 if transaction.days_overdue > 0 else 0
        writer.writerow([
            transaction.transaction_id,
            transaction.student_id.id,
            f"{transaction.student_id.first_name} {transaction.student_id.last_name}",
            transaction.title.title,
            transaction.borrow_date,
            transaction.return_date or 'Not Returned',
            transaction.days_overdue,
            fine_amount,
        ])

    # Get the CSV content from StringIO
    csv_content = csv_file.getvalue()

    # Create the email message
    email = EmailMessage(
        'Transaction Report',  # Subject
        'Please find the attached transaction report.',  # Message
        settings.EMAIL_HOST_USER,  # From email (your email)
        [recipient_email],  # To email(s)
    )
    
    # Attach the CSV file content
    email.attach('transaction_report.csv', csv_content, 'text/csv')
    
    # Send the email
    email.send(fail_silently=False)

    # Respond to the user
    return HttpResponse('Transaction report sent to your email!')
    
    
#@never_cache
#@login_required
def staff_password_change(request):
    if not request.user.is_staff:
        messages.error(request, 'You must be a staff member to access this page.')
        return redirect('staff_books')

    if request.method == 'POST':
        form = StaffPasswordChangeForm(request.POST, instance=request.user)  # Pass the User instance
        if form.is_valid():
            form.save()
            messages.success(request, 'Your password was successfully updated!')
            update_session_auth_hash(request, request.user)  # Keep the user logged in
            return redirect('staff_books')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = StaffPasswordChangeForm(instance=request.user)

    return render(request, 'staff/stpassword.html', {'form': form})

#STUDENT

    #dashboard
#@login_required
#@never_cache
def student_dashboard(request):
    # Get the search query from the GET parameters
    search_query = request.GET.get('search', '')

    # Filter transactions by student_id and optionally by the search query
    transactions = Transaction.objects.filter(student_id=request.user).order_by('-borrow_date')

    if search_query:
        # Apply search filter based on transaction_id or title
        transactions = transactions.filter(
            Q(transaction_id__icontains=search_query) | Q(title__icontains=search_query)
        )

    return render(request, 'student/dashboard.html', {'transactions': transactions})
#@login_required
#@never_cache
def student_books(request):
    query = request.GET.get('q')  # Get the search query from the GET request
    
    if query:
        # Filter books by title or author (case-insensitive search)
        books = Book.objects.filter(
            Q(title__icontains=query) | Q(author__icontains=query)
        )
    else:
        # If no search query, display all books
        books = Book.objects.all()
    
    return render(request, 'student/items.html', {'books': books, 'query': query})
#@login_required
#@never_cache
def shelf_detail(request, pk):
    # Fetch the book using its primary key
    book = get_object_or_404(Book, pk=pk)

    # Retrieve the latest transaction for the book
    transaction = Transaction.objects.filter(
        title=book, 
        return_date__gte=timezone.now().date()  # Ensure the transaction is active (still borrowed)
    ).order_by('-borrow_date').first()

    # Get borrower and overdue days, if a transaction exists
    borrower = transaction.student_id if transaction else None
    overdue_days = transaction.days_overdue if transaction else 0

    # Pass book, borrower, and overdue information to the template
    context = {
        'book': book,
        'borrower': borrower,
        'overdue_days': overdue_days,
    }
    return render(request, 'student/shelfdetail.html', context)
#@never_cache
#@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            # Get the cleaned data from the form
            old_password = form.cleaned_data['old_password']
            new_password = form.cleaned_data['new_password']

            # Set the new password for the user
            user = request.user
            user.set_password(new_password)  # Set the new password
            user.save()  # Save the updated user object

            # Keep the user logged in after password change
            update_session_auth_hash(request, user)

            # Display success message
            messages.success(request, 'Your password was successfully updated!')
            return redirect('student_dashboard')  # Replace with your dashboard URL name
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PasswordChangeForm(user=request.user)

    return render(request, 'student/clpassword.html', {'form': form})


from django.shortcuts import redirect
from django.contrib.auth import logout
from django.utils.cache import patch_cache_control

#@never_cache
def logout_view(request):
    """Logout view for all user types."""
    logout(request)  # Log out the user
    request.session.flush()  # Clear session data

    # Redirect to the landing page after logging out
    response = redirect('landing_page')

    # Add headers to prevent caching
    patch_cache_control(response, no_cache=True, no_store=True, must_revalidate=True)

    return response
