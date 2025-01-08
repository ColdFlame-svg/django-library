
# Create your models here.
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.auth.hashers import make_password, check_password



class UserManager(BaseUserManager):
    def create_user(self, student_id, password=None, **extra_fields):
        if not student_id:
            raise ValueError('The Student ID must be set')
        extra_fields.setdefault('is_admin', False)  # Default to False
        user = self.model(student_id=student_id, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, student_id, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_admin', True)  # Ensure is_admin is True
        return self.create_user(student_id, password, **extra_fields)
class User(AbstractBaseUser):
    SUFFIX_CHOICES = [
        ('Jr', 'Jr.'),
        ('Sr', 'Sr.'),
        ('II', 'II'),
        ('III', 'III'),
        ('IV', 'IV'),
        ('None', 'None'),
    ]
    
    student_id = models.CharField(max_length=50, unique=True, verbose_name="Student ID")
    first_name = models.CharField(max_length=100, verbose_name="First Name")
    middle_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Middle Name")
    last_name = models.CharField(max_length=100, verbose_name="Last Name")
    suffix = models.CharField(max_length=10, choices=SUFFIX_CHOICES, default='None', verbose_name="Suffix")
    email = models.EmailField(unique=True, verbose_name="Email Address")
    password = models.CharField(max_length=128, verbose_name="Password")
    terms_accepted = models.BooleanField(default=False, verbose_name="Terms Accepted")
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'student_id'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'email']  # Add fields required for creating a superuser

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"


class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin', null=True, blank=True)
    admin_id = models.CharField(max_length=50, unique=True, default="TEMP_ADMIN_ID")
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True, null=True)
    password = models.CharField(max_length=128, default=make_password('defaultpassword'))  # Default hashed password
    date_added = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.admin_id})"

    def save(self, *args, **kwargs):
        # Ensure the password is hashed before saving
        if not self.password.startswith('pbkdf2_'):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

class RemovedAdmin(models.Model):
    admin = models.ForeignKey('Admin', on_delete=models.SET_NULL, null=True)
    removed_admin_id = models.CharField(max_length=50, default="UNKNOWN")  # Stores the original Admin ID
    admin_name = models.CharField(max_length=200, default="NULL")  # Store full name as a separate field
    date_removed = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.admin_name} (ID: {self.removed_admin_id}) removed on {self.date_removed}'



class Staff(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='staff', null=True, blank=True)
    staff_id = models.CharField(max_length=50, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128, default=make_password('defaultpassword'))  # Default hashed password
    date_added = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.staff_id})"

    def save(self, *args, **kwargs):
        if not self.password.startswith('pbkdf2_'):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)
    
class RemovedStaff(models.Model):
    staff = models.ForeignKey('Staff', on_delete=models.SET_NULL, null=True)
    removed_staff_id = models.CharField(max_length=50, default="UNKNOWN")  # Stores the original Staff ID
    staff_name = models.CharField(max_length=200, default="NULL")  # Store full name as a separate field
    date_removed = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.staff_name} (ID: {self.removed_staff_id}) removed on {self.date_removed}'

        
class Book(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('borrowed', 'Borrowed'),
        ('archive', 'Archived'),
    ]
    
    isbn = models.CharField(max_length=13)
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    published_date = models.DateField()
    description = models.TextField()
    image = models.ImageField(upload_to='book_covers/', blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='available')  

    def __str__(self):
        return self.title
    
    def update_status(self):
        """
        Update the status of the book based on active transactions.
        If there are no active transactions, mark as 'available'.
        """
        # Check for any active (unreturned) transactions
        active_transaction = self.transaction_set.filter(return_date__gte=timezone.now().date()).exists()
        if active_transaction:
            self.status = 'borrowed'
        else:
            self.status = 'available'
        self.save()
    

class RemovedBook(models.Model):
    book = models.ForeignKey('Book', on_delete=models.SET_NULL, null=True)
    removed_isbn = models.CharField(max_length=13, default="UNKNOWN")  # Stores original ISBN
    title = models.CharField(max_length=255, default="UNKNOWN")  # Stores the book title
    published_date = models.DateField(null=True, blank=True)  # Stores the original published date
    date_removed = models.DateTimeField(default=timezone.now)  # Date the book was removed
    removed_book_id = models.CharField(max_length=50, default="UNKNOWN")  # Stores the original Book ID

    def __str__(self):
        return f'{self.title} (ISBN: {self.removed_isbn}) removed on {self.date_removed}'

class Transaction(models.Model):
    # Fields remain unchanged
    transaction_id = models.CharField(max_length=100, unique=True)
    student_id = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.ForeignKey(Book, on_delete=models.CASCADE)
    borrow_date = models.DateField(default=timezone.now)
    return_date = models.DateField(null=True, blank=True)
    days_overdue = models.IntegerField(default=0)

    def calculate_overdue_days(self):
        """Calculate overdue days based on return_date and current date."""
        if self.return_date:
            overdue_days = (timezone.now().date() - self.return_date).days
            return max(overdue_days, 0)
        else:
            overdue_days = (timezone.now().date() - self.borrow_date).days
            return max(overdue_days, 0)

    def save(self, *args, **kwargs):
        """Override save to calculate overdue days and manage Fine entries."""
        self.days_overdue = self.calculate_overdue_days()
        super().save(*args, **kwargs)  # Save transaction first
        
        # Create or update Fine entry if overdue
        if self.days_overdue > 0:
            Fine.objects.update_or_create(
                transaction=self,
                defaults={
                    'student_id': self.student_id.student_id,
                    'first_name': self.student_id.first_name,
                    'last_name': self.student_id.last_name,
                    'book_title': self.title.title,
                    'date_borrowed': self.borrow_date,
                    'date_returned': self.return_date,
                    'days_overdue': self.days_overdue,
                    'fine_amount': self.days_overdue * 5.0,  # Example fine: $5 per day
                }
            )
        else:
            # If no overdue, delete the Fine entry (if it exists)
            Fine.objects.filter(transaction=self).delete()

    
class Fine(models.Model):
    # Link Fine to a Transaction
    transaction = models.OneToOneField(
    "Transaction",
    on_delete=models.CASCADE,
    related_name="fine",
    null=True,  # Allow nulls temporarily
    blank=True
)
    
    # Student details (can be derived from Transaction)
    student_id = models.CharField(max_length=20, unique=False)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    
    # Book information
    book_title = models.CharField(max_length=200)
    
    # Date information
    date_borrowed = models.DateField()
    date_returned = models.DateField(null=True, blank=True)
    
    # Overdue details
    days_overdue = models.IntegerField()
    fine_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    def __str__(self):
        return f"{self.student_id} - {self.book_title} - {self.days_overdue} days overdue"

    
