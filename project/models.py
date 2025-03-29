from django.db import models
import hashlib
from django.utils.timezone import now
import uuid

class User(models.Model):
    uniqueid = models.CharField(max_length=64, unique=True, null=True)  # Temporarily make it nullable
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15, unique=True)
    password = models.CharField(max_length=255)  # Store hashed password later
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)  # To store the generated QR code
    amount= models.DecimalField(max_digits=10000, decimal_places=2, null=True, blank=True)
    limit= models.DecimalField(max_digits=10000, decimal_places=2, null=True, blank=True)
    

    def save(self, *args, **kwargs):
        # Generate the unique ID based on phone number
        if not self.uniqueid:
            self.uniqueid = self.generate_unique_id_from_phone_number(self.phone_number)
        super(User, self).save(*args, **kwargs)

    def generate_unique_id_from_phone_number(self, phone_number):
        # Create a hash from the phone number to generate a unique id
        return hashlib.sha256(phone_number.encode('utf-8')).hexdigest()

    def __str__(self):
        return self.name

#from django.contrib.auth.models import User


    
class Transaction(models.Model):
    PURPOSE_CHOICES = [
        ('expense', 'Expense'),
        ('sharing', 'Sharing'),
        ('food', 'Food'),
        ('loan', 'Loan'),
        ('education', 'Education'),
        ('other', 'Other'),
    ]
    transaction_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, primary_key=True)
    sender = models.ForeignKey('User', on_delete=models.CASCADE, related_name='sent_transactions')
    sender_phone = models.CharField(max_length=15, null=True, blank=True)  # <-- Added sender_phone
    receiver = models.ForeignKey('User', on_delete=models.CASCADE, related_name='received_transactions')
    receiver_phone = models.CharField(max_length=15, null=True, blank=True)
    sent = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    received = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES, default="other")
    is_bill_split = models.BooleanField(default=False) 

    def save(self, *args, **kwargs):
        """Ensure phone numbers are stored before saving."""
        self.sender_phone = self.sender.phone_number 
        self.receiver_phone = self.receiver.phone_number
        self.received = self.sent  # Ensuring the received amount equals sent amount
        super().save(*args, **kwargs)   
    def __str__(self):
        return f"{self.sender.name} ({self.sender_phone}) {self.sent} to {self.receiver.name} ({self.receiver_phone}) amount{self.sent}"

from django.db import models

class KnowledgeBase(models.Model):
    question = models.CharField(max_length=255, help_text="The question to trigger the response.")
    answer = models.TextField(help_text="The answer to provide when the question is asked.")

    def __str__(self):
        return self.question
