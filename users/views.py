from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.views.decorators.csrf import csrf_protect
from businesses.models import Business  # import your Business model

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()

            # Authenticate the user
            user = authenticate(username=user.username, password=request.POST['password1'])
            login(request, user)

            # Create a default business profile right away
            Business.objects.create(
                owner=user,
                name=f"{user.username}'s Business",
                business_type="shop",  # default type (you can ask in form later)
                phone="",
            )

            return redirect('dashboard:home')  # send them to dashboard
    else:
        form = UserCreationForm()
    return render(request, 'users/register.html', {'form': form})

@csrf_protect
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            if 'next' in request.POST:
                return redirect(request.POST.get('next'))
            else:
                return redirect('dashboard:dashboard')  # redirect to business dashboard
    else:
        form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})

def logout_view(request):
    if request.method=='POST':
        logout(request)
        return redirect('homepage')