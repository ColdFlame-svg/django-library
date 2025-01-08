from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Transaction, Book

@receiver(post_save, sender=Transaction)
def update_book_status(sender, instance, created, **kwargs):
    if created:
        # Get the book related to the transaction
        book = instance.title  # `title` is the foreign key to the Book model

        # Check if the book is not already borrowed
        if book.status != 'borrowed':
            # Update the status to 'borrowed'
            book.status = 'borrowed'
            book.save()  # Save the updated book instance
