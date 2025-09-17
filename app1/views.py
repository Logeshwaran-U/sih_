from django.shortcuts import render
from .models import State_details
from django.db.models import Q

def index(request):
    query = request.GET.get('q')  # Get search query from URL
    if query:
        # Filter states by name (case-insensitive)
        states = State_details.objects.filter(state_name__icontains=query)
    else:
        # If no query, show all states
        states = State_details.objects.all()
    
    return render(request, 'app1/index.html', {'states': states, 'query': query})



from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage, send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.utils.timezone import now
from django.utils.safestring import mark_safe
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse

from .forms import (
    CustomUserCreationForm
)
from .models import CustomUser
from .tokens import account_activation_token


def activateemail(request, user, to_email):
    """Sends an account activation email with a valid token."""

    mail_subject = 'Activate your account'
    
    user_name = getattr(user, "name", "User")
    user.last_login = now()
    user.save(update_fields=["last_login"])  

    token = account_activation_token.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))

    protocol = "https" if request.is_secure() else "http"
    domain = get_current_site(request).domain
    activation_link = f"{protocol}://{domain}{reverse('activate', kwargs={'uidb64': uid, 'token': token})}"

    message = render_to_string("app1/activate_acc.html", {
        'user': user_name,
        'activation_link': activation_link  # Use this directly in the template
    })

    email = EmailMessage(mail_subject, message, from_email="noreply@example.com", to=[to_email])
    email.content_subtype = "html"

    try:
        if email.send():
            message_text = f'Dear <b>{user_name}</b>, we have sent a link to your email: <b>{to_email}</b>'
            messages.success(request, mark_safe(message_text))
        else:
            messages.error(request, 'Problem sending email. Please try again later.')
    except Exception as e:
        messages.error(request, f"Error sending email: {str(e)}")

def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    if user and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Thank you for email confirmation. Your account is now activated.")
        return redirect('login_page')
    else:
        messages.error(request, "Invalid or expired activation link. Please request a new one.")
        return redirect('resend_acc')


def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get("email")
            existing_users = CustomUser.objects.filter(email=email)

            if existing_users.exists():
                user = existing_users.first()
                if user.is_active:
                    msg = "This email is already activated. Please log in."
                    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                        return JsonResponse({"success": False, "errors": [msg]})
                    messages.info(request, msg)
                    return redirect("login_")
                else:
                    msg = "This email is registered but not activated. Resending activation link."
                    activateemail(request, user, email)
                    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                        return JsonResponse({"success": False, "errors": [msg]})
                    messages.info(request, msg)
                    return redirect("resend_acc")
            else:
                user = form.save(commit=False)
                user.is_active = False
                user.save()
                activateemail(request, user, email)

                if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                    return JsonResponse({"success": True, "redirect_url": reverse('index')})
                return redirect("index")
        else:
            
            errors = []
            for field, error_messages in form.errors.items():
                for error in error_messages:
                    errors.append(f"{field}: {error}")

            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse({"success": False, "errors": errors, "old_values": request.POST.dict()})
    
    else:
        form = CustomUserCreationForm()

    return render(request, "app1/register_user.html", {"form": form})


def login_page(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        try:
            user = CustomUser.objects.get(email=email)
            
            if not user.is_active:
                return JsonResponse({'success': False, 'error': "Your account is not activated yet. Please check your email."})
            
            user = authenticate(request, username=email, password=password)
            
            if user is not None:
                login(request, user)
                return JsonResponse({'success': True, 'redirect_url': '/'})
            else:
                return JsonResponse({'success': False, 'error': "Invalid email or password."})
                
        except CustomUser.DoesNotExist:
            return JsonResponse({'success': False, 'error': "Invalid email or password."})

    return render(request, 'app1/login_.html')

def state_details(request, slug):
    state = get_object_or_404(State_details, slug=slug)
    music_list = state.music.all()        # related_name="music"
    festival_list = state.festivals.all() # related_name="festivals"

    return render(request, "app1/state_details.html", {
        "state": state,
        "music_list": music_list,
        "festival_list": festival_list,
    })

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
from .forms import StateMusicForm, StateFestivalForm

# Only allow staff (admin) users
def is_admin(user):
    return user.is_staff or user.is_superuser


@user_passes_test(is_admin)
def add_music(request):
    if request.method == "POST":
        form = StateMusicForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("state_details")
    else:
        form = StateMusicForm()
        print("went wrong")
    return render(request, "app1/add_state_music.html", {"form": form})


@user_passes_test(is_admin)
def add_festival(request):
    if request.method == "POST":
        form = StateFestivalForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("state_details")
    else:
        form = StateFestivalForm()
        print("wnet wrong")
        
    return render(request, "app1/add_state_festival.html", {"form": form})
