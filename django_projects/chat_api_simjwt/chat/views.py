# chat/views.py
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .forms import LoginForm, UserRegistrationForm


from .models import Room


@login_required
def index_view(request):
    return render(request, 'index.html', {
        'rooms': Room.objects.all(),
    })


@login_required
def room_view(request, room_name):

    chat_room, created = Room.objects.get_or_create(name=room_name)

    return render(request, 'room.html', {
        'room': chat_room,
    })


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request,
                                username=cd['username'],
                                password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponse('Authenticated successfully')
                else:
                    return HttpResponse('Disabled account')
            else:
                return HttpResponse('Invalid login')
    else:
        form = LoginForm()
    return render(request, 'account/login.html', {'form': form})


def handler404(request, *args, **argv):
    response = render(request, '404.html')
    response.status_code = 404

    return response


def register(request):

    if request.method == 'POST':
        
        user_form = UserRegistrationForm(request.POST)

        if user_form.is_valid():
            # Create a new user object but avoid saving it yet
            new_user = user_form.save(commit=False)
            # Set the chosen password
            new_user.set_password(
                user_form.cleaned_data['password'])
            # Save the User object
            new_user.save()
            
            return render(request,
                        'account/register_done.html',
                        {'new_user': new_user})
        else:
            return HttpResponse('Your invalid')
    else:
        user_form = UserRegistrationForm()
        return render(request,
                    'account/register.html',
                    {'user_form': user_form})
