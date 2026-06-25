from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now
from django.http import JsonResponse
from datetime import timedelta
from .models import UserProfile, Membership, Activity, Booking, Attendance, Reward, SmartContractExecution
from django.contrib import messages
import uuid, json, math

#Sports Park
# TARGET_LAT = 50.7380364
# TARGET_LON = -3.5397418

TARGET_LAT = 50.7347323
TARGET_LON = -3.5285962

membership_status = {'Active': True, 'Pending': False, 'Inactive':False}

def send_tokens(request):
    # if request.user.is_authenticated:
    #     return render(request, 'base_dashboard.html')  # If logged in, go to Dashboard
    return render(request, 'send_tokens.html')

def home(request):
    if request.user.is_authenticated:
        return render(request, 'base_dashboard.html')  # If logged in, go to Dashboard
    return render(request, 'home.html')

# User Registration
def register_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        if User.objects.filter(username=username).exists():
            messages.error(request, "This email is already registered. Please login.")
            return redirect('login')
        user = User.objects.create_user(username=username, password=password)
        user.save()
        UserProfile.objects.create(user=user)  # Create a profile for user
        #Membership.objects.create(membership_status='Inactive')  
        messages.success(request, "Registration successful! Please log in.")
        return redirect('login')
    return render(request, 'register.html')

# User Login
def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid credentials")
    return render(request, 'login.html')

def dashboard(request):
    return render(request, 'base_dashboard.html')  # If logged in, go to Dashboard

# User Logout
@login_required
def logout_user(request):
    logout(request)
    request.session.flush()
    return redirect('login')

# Dashboard (Membership & Activity Overview)
# @login_required
def membership(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    if request.method =='POST':
        data = json.loads(request.body)
        tx_hash = data.get('transaction_hash')
        if tx_hash:
            #membership_obj = Membership.objects.create(price = 0.05, tx_hash = tx_hash, membership_status = 'Active')
            membership_obj = Membership.objects.create(
                name="yearly",
                price=0.05,
                tx_hash=tx_hash,
                membership_status='Active'
            )
            user_profile.membership = membership_obj
            user_profile.membership_start = now().date()
            user_profile.membership_end = now().date() + timedelta(days=365)
            user_profile.save()
            messages.success(request, f"Membership bought successfully!")
            print(membership_obj.tx_hash)
            print(user_profile.membership_start,user_profile.membership_end, user_profile.is_membership_active())
            return JsonResponse({'status': 'success', 'tx_hash': tx_hash})
        else:
            return JsonResponse({'status': 'error', 'message': 'No transaction hash provided'})

    return render(request, 'membership.html', {'profile': user_profile})

# Buy Yearly Membership
# @login_required
# def buy_membership(request):
#     membership = Membership.objects.filter(name="yearly").first()
#     if membership:
#         messages.error(request, "Already a member!")
#         return redirect('dashboard')

#     user_profile = get_object_or_404(UserProfile, user=request.user)
#     user_profile.membership = membership
#     user_profile.membership_start = now().date()
#     user_profile.membership_end = now().date() + timedelta(days=365)
#     user_profile.save()

#     messages.success(request, "Yearly membership purchased successfully!")
#     return redirect('dashboard')

# List Available Activities
@login_required
def activity_list(request):
    activities = Activity.objects.all()
    return render(request, 'activities.html', {'activities': activities})

# Book an Activity
@login_required
def book_activity(request, activity_id):
    activity = get_object_or_404(Activity, id=activity_id)
    booking = Booking.objects.create(user=request.user, activity=activity, date=now().date(), time=now().time())
    messages.success(request, f"Booked {activity.name} successfully!")
    return redirect('dashboard')

# Cancel a Booking
@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    booking.status = "cancelled"
    booking.save()
    messages.success(request, "Booking cancelled successfully!")
    return redirect('dashboard')

# Check-in (Mark Attendance with Location)
# @login_required
# def check_in(request):
#     if request.method == "POST":
#         latitude = request.POST.get('latitude')
#         longitude = request.POST.get('longitude')
#         activity_id = request.POST.get('activity_id')
#         activity = get_object_or_404(Activity, id=activity_id)

#         Attendance.objects.create(user=request.user, activity=activity, location_lat=latitude, location_long=longitude)

#         # Track Attendance for Rewards
#         track_rewards(request.user)

#         messages.success(request, f"Checked in for {activity.name} successfully!")
#         return redirect('dashboard')
#     return render(request, 'checkin.html')

@csrf_exempt
def checkin(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_lat = data.get('latitude')
        user_lon = data.get('longitude')
        user_profile = get_object_or_404(UserProfile, user=request.user)
        # Calculate distance from target location
        distance = calculate_distance(user_lat, user_lon, TARGET_LAT, TARGET_LON)

        # Check if the user is within 100 meters of the target location
        if distance <= 500:
            if user_profile.check_in_count == 3:
                user_profile.check_in_count = 0
                user_profile.save()
                message = "Congratulations! Rewards Credited!"
            else:
                user_profile.check_in_count += 1
                user_profile.save()
                message = "Check-in successful! You are at the correct location."
        else:
            message = f"Check-in failed. You are {distance:.2f} meters away from the target location."

        return JsonResponse({'message': message})

    return render(request, 'checkin.html')


# Function to calculate distance between two coordinates (in meters)
def calculate_distance(lat1, lon1, lat2, lon2):
    # Haversine formula
    R = 6371000  # Radius of the Earth in meters
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    a = math.sin(dLat / 2) * math.sin(dLat / 2) + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dLon / 2) * math.sin(dLon / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return distance

# Track & Reward Users (4 times per week)
# def track_rewards(user):
#     today = now().date()
#     week_start = today - timedelta(days=today.weekday())  # Monday of current week
#     week_end = week_start + timedelta(days=6)  # Sunday of current week

#     workouts_count = Attendance.objects.filter(user=user, checkin_time__date__range=[week_start, week_end]).count()

#     reward, created = Reward.objects.get_or_create(user=user, week_start=week_start, week_end=week_end)
#     reward.workouts_count = workouts_count
#     reward.check_eligibility()
    
#     if reward.reward_earned:
#         execute_smart_contract(user, reward)

# Execute Smart Contract (Ethereum Rewards) [Placeholder]
def execute_smart_contract(user, reward):
    transaction_hash = str(uuid.uuid4())[:66]  # Placeholder for Ethereum transaction
    SmartContractExecution.objects.create(user=user, reward=reward, transaction_hash=transaction_hash)
    return render('send_tokens.html')

# View Rewards
@login_required
def view_rewards(request):
    rewards = Reward.objects.filter(user=request.user)
    return render(request, 'rewards.html', {'rewards': rewards})
