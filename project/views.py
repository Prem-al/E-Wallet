import qrcode
from django.shortcuts import render, redirect
from django.conf import settings
from .forms import UserRegistrationForm
from .models import User
from django.contrib.auth.hashers import make_password, check_password


def dashboard_view(request):
    return render(request, 'dashboard.html')

from django.contrib.auth.hashers import make_password
def register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # Save the user to the database
            name = form.cleaned_data['name']
            phone_number = form.cleaned_data['phone_number']
            password = form.cleaned_data['password']  # In a real app, hash the password
            
            hashed_password=make_password(password)
            # Create the User instance
            user = User(name=name, phone_number=phone_number, hashed_password=password)
            user.save()  # The ID will be auto-assigned by Django

            # Generate the unique QR code based on phone number
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(phone_number)
            qr.make(fit=True)

            # Create an image from the QR code
            img = qr.make_image(fill='black', back_color='white')

            # Save the QR code image
            qr_code_path = f'{settings.MEDIA_ROOT}/qr_codes/{user.id}_qr.png'
            img.save(qr_code_path)

            # Save the QR code path in the user model
            user.qr_code = f'qr_codes/{user.id}_qr.png'
            user.save()

            return redirect('login')  # Redirect to the login page or wherever you want
    else:
        form = UserRegistrationForm()

    return render(request, 'register.html', {'form': form})

from django.contrib.auth.hashers import check_password
from django.shortcuts import render, redirect
from .models import User

def login(request):
    error = None  # Initialize error as None or empty string
    
    if request.method == "POST":
        phone_number = request.POST.get("phone_number")  # Use get to avoid KeyError
        password = request.POST.get("password")

        print(f"Phone Number: {phone_number}, Password: {password}")  # Debug line
        
        if phone_number and password:  # Check if both phone_number and password are provided
            try:
                user = User.objects.get(phone_number=phone_number)
                print(f"User found: {user}")  # Debug line
                
                if check_password(password, user.password):  # Check hashed password
                    return redirect('dashboard')  # Redirect to 'dashboard' view after successful login
                else:
                    error = "Invalid phone number or password"
            except User.DoesNotExist:
                error = "User does not exist"
        else:
            error = "Please provide both phone number and password"

    return render(request, "login.html", {"error": error})




from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.http import HttpResponse
from .forms import SendMoneyForm
from .models import User, Transaction
from django.utils.timezone import now

def send_moneyss(request):
    if request.method == "POST":
        form = SendMoneyForm(request.POST)
        
        # Check if the form is valid
        if form.is_valid():
            sender_phone = form.cleaned_data["sender_phone"]
            receiver_phone = form.cleaned_data["receiver_phone"]
            amount = form.cleaned_data["amount"]

            # Retrieve sender and receiver from the database
            try:
                sender = User.objects.get(phone_number=sender_phone)
                receiver = User.objects.get(phone_number=receiver_phone)
            except User.DoesNotExist:
                return JsonResponse({"error": "Sender or Receiver not found"}, status=400)

            # Check if sender has sufficient balance
            if sender.amount < amount:
                return JsonResponse({"error": "Insufficient balance"}, status=400)

            # Check if amount exceeds sender's limit
            if amount > sender.limit:
                return JsonResponse({"error": "Amount exceeds daily transaction limit"}, status=400)

            # Perform the transaction
            sender.amount -= amount
            sender.save()

            receiver.amount += amount
            receiver.save()

            # Create a transaction record
            transaction = Transaction.objects.create(
                sender=sender,
                sender_phone=sender.phone_number,
                receiver=receiver,
                receiver_phone=receiver.phone_number,
                sent=amount,        # Amount sent is added directly here
                received=amount,    # Amount received is added directly here
                date=now()          # Current date and time
            )

            return HttpResponse({"Transaction successful"})

        else:
            return JsonResponse({"error": "Invalid form data"}, status=400)
    
    else:
        form = SendMoneyForm()

    return render(request, 'send_money.html', {'form': form})


from django.shortcuts import render
from .models import KnowledgeBase
from .forms import ChatForm

def chatbot(request):
    response = ""
    user_input = ""

    if request.method == "POST":
        form = ChatForm(request.POST)
        if form.is_valid():
            user_input = form.cleaned_data['user_input']
            
            # Search for the question in the knowledge base
            try:
                # Find the answer based on user input (case-insensitive search)
                kb_entry = KnowledgeBase.objects.filter(question__icontains=user_input).first()
                if kb_entry:
                    response = kb_entry.answer
                else:
                    response = "Sorry, I couldn't find an answer to your question. Please conatct our support team at support@ewallet.com"
            except Exception as e:
                response = "Please Contact our teachnical team for this issue."

    else:
        form = ChatForm()

    return render(request, 'chatbot.html', {'form': form, 'response': response, 'user_input': user_input})

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import User, Transaction
from .forms import BillSplitForm
import uuid
from django.utils.timezone import now

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import User, Transaction
from .forms import BillSplitForm
import uuid
from django.utils.timezone import now

def split_bill(request):
    if request.method == "POST":
        form = BillSplitForm(request.POST)
        if form.is_valid():
            bill_amount = form.cleaned_data["bill_amount"]
            participants_phones = form.cleaned_data["participants_phones"]
            merchant_phone = form.cleaned_data["merchant_phone"]

            # Get the list of registered users and merchant by phone number
            participants = [get_object_or_404(User, phone_number=phone) for phone in participants_phones]
            merchant = get_object_or_404(User, phone_number=merchant_phone)

            # Split the bill equally among participants
            per_person_amount = bill_amount / len(participants)
            transactions = []

            # Process each participant (user) who will pay
            for user in participants:
                if user.amount >= per_person_amount:
                    # Deduct from user
                    user.amount -= per_person_amount
                    user.save()

                    # Add to merchant (receiver)
                    merchant.amount += per_person_amount
                    merchant.save()

                    # Create a transaction entry
                    transaction = Transaction.objects.create(
                        transaction_id=uuid.uuid4(),  # Unique ID
                        sender=user,
                        sender_phone=user.phone_number,
                        receiver=merchant,
                        receiver_phone=merchant.phone_number,
                        sent=per_person_amount,
                        received=per_person_amount,
                        date=now()
                    )
                    transactions.append(transaction.transaction_id)
                else:
                    return JsonResponse({"error": f"{user.name} does not have enough balance!"})

            return JsonResponse({"success": "Bill split successfully!", "transactions": transactions})

    else:
        form = BillSplitForm()

    return render(request, "split_bill.html", {"form": form})
# from django.shortcuts import render, redirect
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from django.contrib.auth.decorators import login_required
# import json
# import re
# from django.db.models import Q 

# from django.contrib.auth import get_user_model

# @login_required
# def add_contact(request):
#     User = get_user_model()  # Get the actual User class
    
#     if request.method == 'POST':
#         recipient_identifier = request.POST.get('recipient_identifier')
#         nickname = request.POST.get('nickname')
        
#         try:
#             # Ensure we have a proper User instance
#             owner = User.objects.get(pk=request.user.pk)
            
#             recipient = User.objects.get(
#                 Q(uniqueid=recipient_identifier) |
#                 Q(phone_number=recipient_identifier) |
#                 Q(name__iexact=recipient_identifier)
#             )
            
#             Contact.objects.create(
#                 owner=owner,
#                 saved_user=recipient,
#                 nickname=nickname
#             )
#             return redirect('contacts_list')
            
#         except User.DoesNotExist:
#             return render(request, 'add_contact.html', {'error': 'User not found'})
#         except User.MultipleObjectsReturned:
#             return render(request, 'add_contact.html', {'error': 'Multiple users found'})
    
#     return render(request, 'add_contact.html')

# # Voice Command Processing
# @csrf_exempt
# @login_required
# def voice_transfer(request):
#     if request.method == 'POST':
#         try:
#             data = json.loads(request.body)
#             voice_text = data.get('voice_text', '').lower().strip()
            
#             # Parse command with more flexible regex
#             match = re.match(r"^(send|pay|transfer)\s+(?:rs\.?|₹|inr)?\s*(\d+)\s+(?:to|for)\s+(\w+)", voice_text)
#             if not match:
#                 return JsonResponse({
#                     'error': 'Invalid format. Try: "Send 500 to John" or "Pay ₹1000 to Mom"'
#                 }, status=400)
            
#             amount, contact_name = match.group(2), match.group(3)
            
#             # Find contact (case-insensitive)
#             try:
#                 contact = Contact.objects.get(
#                     owner=request.user,
#                     nickname__iexact=contact_name
#                 )
                
#                 # Check sender's balance
#                 if request.user.amount < float(amount):
#                     return JsonResponse({
#                         'error': f'Insufficient balance. You only have ₹{request.user.amount}'
#                     }, status=400)
                
#                 # Check transaction limit
#                 if float(amount) > request.user.limit:
#                     return JsonResponse({
#                         'error': f'Amount exceeds your limit of ₹{request.user.limit}'
#                     }, status=400)
                
#                 # Create transaction
#                 Transaction.objects.create(
#                     sender=request.user,
#                     receiver=contact.saved_user,
#                     amount=amount
#                 )
                
#                 # Update balances
#                 request.user.amount -= float(amount)
#                 request.user.save()
#                 contact.saved_user.amount += float(amount)
#                 contact.saved_user.save()
                
#                 return JsonResponse({
#                     'success': f'₹{amount} sent to {contact.nickname}',
#                     'balance': f'New balance: ₹{request.user.amount}'
#                 })
                
#             except Contact.DoesNotExist:
#                 return JsonResponse({
#                     'error': f'No contact named "{contact_name}". Add them first.'
#                 }, status=404)
            
#         except Exception as e:
#             return JsonResponse({
#                 'error': f'Processing error: {str(e)}'
#             }, status=500)
        
# from django.contrib.auth import authenticate,login
# from django.shortcuts import HttpResponse
 
# def home(request):
#     if request.method=="POST":
#         phone = request.POST.get('phone')
#         password = request.POST.get('password')

#         user = authenticate(request, username=phone, password=password)
#         if user is not None:
#             return redirect('adminview')  
#         else:
#             messages.error(request, "Invalid username or password")
#     return render(request, 'home.html')        
from django.contrib import messages
def home(request):
    error = None  # Initialize error as None or empty string
    
    if request.method == "POST":
        print("this is logged in.")
        phone = request.POST.get("phone")  # Use get to avoid KeyError
        password = request.POST.get("password")

        print(f"Phone Number: {phone}, Password: {password}")  # Debug line
        
        if phone and password:  # Check if both phone_number and password are provided
            try:
                user = User.objects.get(phone_number=phone)
                print(f"User found: {user}")  # Debug line
                
                if (phone==user.phone_number,password==user.password):  # Check hashed password
                    return redirect('dashboard')  # Redirect to 'dashboard' view after successful login
                else:
                     messages.error(request, "Invalid username or password")
            except User.DoesNotExist:
                 messages.error(request, "User Doesn't Exist")
        else:
             messages.error(request, "Please provide both phone number and password")

    return render(request, "home.html", {"error": error})

from django.shortcuts import render
from django.db.models import Sum
from .models import Transaction, User

def dashboard(request):
    user = request.user
    name=user.name
    print(name)  # Get the logged-in user
    transactions = Transaction.objects.filter(sender=user).order_by('-date')[:5]

    sent = Transaction.objects.filter(sender=user).aggregate(Sum('sent'))['sent__sum'] or 0
    received = Transaction.objects.filter(receiver=user).aggregate(Sum('received'))['received__sum'] or 0

    balance = received - sent
    money = user.amount  # Correct way to get the user's balance

    context = {
        'transactions': transactions,
        'balance': balance,
        'money': money
    }
    return render(request, 'dashboard.html', context)



def topup(request):
    if request.method == "POST":
        to_number=9840559633
        message_body="Hello Dear Anil. You have transferred Rs 49.03. Thank You!"
        twilio_send_sms(to_number, message_body)

    return render(request,"topup.html")
def transaction(request):
    return render(request,"transaction.html")
def profile(request):
    return render(request,"profile.html")
    

import cv2
import numpy as np
from pyzbar import pyzbar
from django.http import JsonResponse
from django.shortcuts import render

def scan_qr_page(request):
    """ Render the QR scanner page """
    return render(request, 'scan_qr.html')

def scan_qr_code(request):
    """ QR code scanning function """
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        return JsonResponse({"error": "Could not access the camera"}, status=500)

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                return JsonResponse({"error": "Failed to capture frame"}, status=500)

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            decoded_objects = pyzbar.decode(gray)

            for obj in decoded_objects:
                qr_data = obj.data.decode('utf-8')
                
                # Release the camera and return scanned data
                cap.release()
                cv2.destroyAllWindows()
                return JsonResponse({"qr_data": qr_data})
            
            # Show frame (for debugging - remove in production)
            cv2.imshow('QR Scanner', frame)

            # Close on 'q' key press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

    finally:
        cap.release()
        cv2.destroyAllWindows()

    return JsonResponse({"error": "No QR code detected"}, status=400)

from . forms import PhoneNumberForm
def transaction_history(request):
    transactions = None
    phone_number = None

    if request.method == 'POST':
        form = PhoneNumberForm(request.POST)
        if form.is_valid():
            phone_number = form.cleaned_data['phone_number']
            transactions = Transaction.objects.filter(sender_phone=phone_number) | Transaction.objects.filter(receiver_phone=phone_number)

    else:
        form = PhoneNumberForm()

    return render(request, 'transaction_history.html', {'form': form, 'transactions': transactions, 'phone_number': phone_number})




# from twilio.rest import Client

# def twilio_send_sms(to_number, message_body):
   
#     # Twilio credentials
#     account_sid = "Twilio"
#     auth_token = "Twilio"
#     twilio_number = "Twilio"

#     # Initialize Twilio Client
#     client = Client(account_sid, auth_token)

#     # Send SMS
#     message = client.messages.create(
#         body=message_body,
#         from_=twilio_number,
#         to=to_number
#     )

#     print(f"Message sent successfully! SID: {message.sid}")
#     return message.sid  # Returning SID for tracking

# # Example Usage

# twilio_send_sms("Twilio", "Hello! Twilio ho")