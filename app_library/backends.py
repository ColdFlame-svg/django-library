from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.hashers import check_password
from django.contrib.auth import get_user_model
from .models import Staff

User = get_user_model()

class StudentAuthenticationBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        # Authenticate using the User model (students)
        try:
            user = User.objects.get(student_id=username)
            if user and check_password(password, user.password):
                return user
        except User.DoesNotExist:
            return None

        return None

class StaffAuthenticationBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        # Authenticate using the Staff model (staff)
        try:
            staff = Staff.objects.get(staff_id=username)
            if staff and check_password(password, staff.password):
                # Check if the staff already has a linked User account
                user = User.objects.filter(student_id=staff.staff_id).first()
                if not user:
                    # Create a new User if none is found
                    user = User.objects.create_user(
                        student_id=staff.staff_id,  # Using staff_id as student_id
                        password=password,
                        first_name=staff.first_name,
                        last_name=staff.last_name,
                        email=staff.email,
                        is_staff=True,  # Mark the user as a staff
                    )
                return user
        except Staff.DoesNotExist:
            return None

        return None
