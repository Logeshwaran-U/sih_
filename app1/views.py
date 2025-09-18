from django.shortcuts import render
from .models import State_details,CommunityData
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

from django.shortcuts import render, get_object_or_404
from .models import State_details
from django.shortcuts import render, get_object_or_404
from .models import State_details, CommunityData

def state_details(request, slug):
    state = get_object_or_404(State_details, slug=slug)

    # Using related names to fetch data
    songs = state.music.all()         # from related_name="music"
    festivals = state.festivals.all() # from related_name="festivals"
    community_posts = state.community_posts.all().order_by("-created_at")  # from related_name="community_posts"

    context = {
        "state": state,
        "songs": songs,
        "festivals": festivals,
        "community_posts": community_posts,
    }
    return render(request, "app1/state_details.html", context)


def is_admin(user):
    return user.is_staff or user.is_superuser



# views.py
from django.shortcuts import render, redirect, get_object_or_404
from .models import State_details,StateMusic,StateFestival
from .forms import StateMusicForm, StateFestivalForm,CommunityDataForm

def add_festival(request, state_id):
    state = get_object_or_404(State_details, id=state_id)
    if request.method == "POST":
        form = StateFestivalForm(request.POST, request.FILES)
        if form.is_valid():
            festival = form.save(commit=False)
            festival.state = state   # auto-assign
            festival.save()
            return redirect("state_details", slug=state.slug)
    else:
        form = StateFestivalForm(initial={"state": state})
    return render(request, "app1/add_festival.html", {"form": form, "state": state})


def add_music(request, state_id):
    state = get_object_or_404(State_details, id=state_id)
    if request.method == "POST":
        form = StateMusicForm(request.POST, request.FILES)
        if form.is_valid():
            music = form.save(commit=False)
            music.state = state   # auto-assign
            music.save()
            return redirect("state_details", slug=state.slug)
    else:
        form = StateMusicForm(initial={"state": state})
    return render(request, "app1/add_music.html", {"form": form, "state": state})


def update_music(request, pk):
    music = get_object_or_404(StateMusic, pk=pk)
    state = music.state  # get related state

    if request.method == "POST":
        form = StateMusicForm(request.POST, request.FILES, instance=music)
        if form.is_valid():
            form.save()
            return redirect('state_details', slug=state.slug) 
    else:
        form = StateMusicForm(instance=music)

    return render(request, "app1/update_music.html", {"form": form, "state": state, "music": music})

def update_festival(request, pk):
    festival = get_object_or_404(StateFestival, pk=pk)
    state = festival.state

    if request.method == "POST":
        form = StateFestivalForm(request.POST, request.FILES, instance=festival)
        if form.is_valid():
            form.save()
            return redirect('state_details', slug=state.slug) 
    else:
        form = StateFestivalForm(instance=festival)

    return render(request, "app1/update_festival.html", {"form": form, "state": state, "festival": festival})



# State-specific post
def add_state_post(request, slug):
    state = get_object_or_404(State_details, slug=slug)
    if request.method == "POST":
        form = CommunityDataForm(request.POST, request.FILES, hide_state=True)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.state = state
            post.save()
            return redirect('state_details', slug=state.slug)
    else:
        form = CommunityDataForm(hide_state=True)
    return render(request, "app1/add_post.html", {"form": form, "state": state})

# Global post
def add_global_post(request):
    if request.method == "POST":
        form = CommunityDataForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return redirect('community_global')
    else:
        form = CommunityDataForm()
    return render(request, "app1/add_post.html", {"form": form})

def update_global_post(request, pk):
    post = get_object_or_404(CommunityData, pk=pk)

    # Optional: Only allow the author to update
    if post.user != request.user:
        return redirect('community_global')

    if request.method == 'POST':
        form = CommunityDataForm(request.POST, request.FILES, instance=post, hide_state=False)
        if form.is_valid():
            form.save()
            return redirect('community_global')
    else:
        form = CommunityDataForm(instance=post, hide_state=False)  # show state dropdown

    return render(request, 'app1/update_global_post.html', {'form': form, 'post': post})


# Display all global community posts
def community_global(request):
    category = request.GET.get("category")  # fetch category from URL query
    search_query = request.GET.get("search")  # optional search filter (if you want later)

    posts = CommunityData.objects.all().order_by("-created_at")

    # filter by category if present
    if category:
        posts = posts.filter(category=category)

    # filter by search (optional)
    if search_query:
        posts = posts.filter(title__icontains=search_query)

    categories = dict(CommunityData.CATEGORY_CHOICES)  # so we can loop in template

    context = {
        "posts": posts,
        "categories": categories,
        "current_category": category,
        "search_query": search_query,
    }
    return render(request, "app1/community_global.html", context)


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import UserUpdateForm

@login_required
@login_required
@login_required
def edit_profile(request):
    user = request.user  # current logged-in user

    if request.method == "POST":
        form = UserUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = UserUpdateForm(instance=user)  # ✅ prefill here

    return render(request, 'app1/edit_profile.html', {'form': form, 'user': user})








"""appi"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .tasks import generate_culture_story_task, generate_story_task
from celery.result import AsyncResult
from django.shortcuts import render

@csrf_exempt
def generate_story(request):
    data = json.loads(request.body)
    task = generate_story_task.delay(data.get("prompt"))
    return JsonResponse({"task_id": task.id})

def get_story_result(request, task_id):
    result = AsyncResult(task_id)
    if result.state == "PENDING":
        return JsonResponse({"status": "pending"})
    elif result.state == "SUCCESS":
        return JsonResponse({"status": "success", "data": result.result})
    else:
        return JsonResponse({"status": "error", "message": str(result.info)})

def story_page(request):
    return render(request, "app1/story.html")


from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.conf import settings
from .forms import ImageUploadForm
from .tasks import image_to_culture_task
from celery.result import AsyncResult
import os

@csrf_exempt
def image_to_culture(request):
    if request.method == "POST":
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            img = form.cleaned_data["image"]

            # Save file in MEDIA_ROOT/uploads
            relative_path = os.path.join("uploads", img.name)
            absolute_path = os.path.join(settings.MEDIA_ROOT, relative_path)
            os.makedirs(os.path.dirname(absolute_path), exist_ok=True)

            with open(absolute_path, "wb+") as dest:
                for chunk in img.chunks():
                    dest.write(chunk)

            # Send absolute path to Celery
            task = image_to_culture_task.delay(absolute_path)
            return JsonResponse({"task_id": task.id, "status": "processing"})
    else:
        form = ImageUploadForm()
    return render(request, "app1/image_upload.html", {"form": form})


def get_image_culture_result(request, task_id):
    result = AsyncResult(task_id)
    if result.state == "PENDING":
        return JsonResponse({"status": "pending"})
    elif result.state == "SUCCESS":
        return JsonResponse({"status": "success", "data": result.result})
    else:
        return JsonResponse({"status": "error", "message": str(result.info)})
    
# app1/views.py
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from celery.result import AsyncResult
from .tasks import generate_culture_story_task
from django.conf import settings
from celery import Celery

# Use your Celery app instance
app = Celery('app1')

@csrf_exempt
def generate_culture_story(request):
    if request.method == "POST":
        try:
            body = json.loads(request.body.decode("utf-8"))
            object_name = body.get("object_name", "Cultural Artifact")
            description = body.get("description", "Traditional cultural object")
            history = body.get("history", "It has been part of Indian heritage for centuries.")

            task = generate_culture_story_task.delay(object_name, description, history)
            return JsonResponse({"task_id": task.id})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Only POST allowed"}, status=405)


def get_culture_story_result(request, task_id):
    try:
        result = AsyncResult(task_id)
        if result.state == "PENDING":
            return JsonResponse({"status": "pending"})
        elif result.state == "SUCCESS":
            return JsonResponse({"status": "success", "data": result.result})
        else:
            return JsonResponse({"status": result.state, "error": str(result.result)})
    except Exception as e:
        return JsonResponse({"status": "error", "error": str(e)})


from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

# Import the synchronous helper from tasks (see tasks.py below)
from .tasks import generate_3d_model_sync

def generate_3d_page(request):
    # Renders the template at app1/templates/app1/generate_3d.html
    return render(request, "app1/generate_3d.html")


@csrf_exempt
def generate_3d_model_view(request):
    # API: accepts POST JSON {"prompt": "..."} and returns {"model_url": "..."}
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method — POST required"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))
    except Exception:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    prompt = data.get("prompt")
    if not prompt:
        return JsonResponse({"error": "No prompt provided"}, status=400)

    try:
        # Synchronous call to Meshy (blocks until model ready or timeout).
        model_url = generate_3d_model_sync(prompt)
        return JsonResponse({"model_url": model_url})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

