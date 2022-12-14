import json

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import *
from django.forms.models import fields_for_model
from django.forms import ValidationError
from django.forms import formset_factory

from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from transaction.models import Transaction
from django.apps import apps

from django.utils.datastructures import MultiValueDictKeyError


from .models import Employee
from .forms import *
from product.forms import *

# Create your views here.


def login_view(request):
    context = {'title': 'Login', 'next': ''}
    # Login
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.info(request, 'Username or Password correct')
            if request.POST["next"]:
                return redirect(request.POST["next"])
            else:
                return redirect('dashboard')
        else:
            context['error_message'] = 'invalid username or password'
            messages.info(request, 'Username or Password incorrect')
    elif request.method == "GET" and "next" in request.GET:
        context["next"] = request.GET["next"]

    return render(request, 'login.html', context)


@login_required(login_url='login')
def test_login(request):
    print(request.user.is_authenticated)
    print(request.user.username)

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required(login_url='login')
def dashboard_view(request):
    context={'title':'Dashboard'}
    return render(request, 'index.html',context)

@login_required(login_url='login')
@permission_required('employee.view_management', raise_exception=True)
def management_view(request):
    context={'title':'Management'}
    return render(request, 'management.html', context)


@login_required(login_url='login')
@permission_required('employee.register_user', raise_exception=True)
def register_view(request):
    if request.method == 'GET':
        user_form = User_Registration_Form()
        profile_form = Employee_Registration_Form()
        try:
            department = request.GET['department']
            profile_form.fields['department'].validate(department)
            profile_form.initial['department'] = department
        except MultiValueDictKeyError:
            return redirect('choose')
        except ValidationError:
            return redirect('choose')

        context = {'user_form':user_form, 'department':department, 'profile_form':profile_form, 'title':'Management'}
        return render(request, 'management/CreateNewAcc.html', context)

    elif request.method == 'POST':
        user_form = User_Registration_Form(request.POST)
        profile_form = Employee_Registration_Form(request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            employee = profile_form.save(commit=False)
            employee.user = user
            employee.update_permission()
            employee.save()
            return redirect('management')
            
        else:
            context = {'user_form':user_form, 'profile_form':profile_form, 'department':request.POST['department'], 'title':'Management'}
            return render(request, 'management/CreateNewAcc.html', context)


@login_required(login_url='login')
@permission_required('employee.register_user', raise_exception=True)
def choose_user_view(request):
    context = {'title':'Management'}
    return render(request, 'management/ChooseUser.html', context)

def permission_denied_view(request):
    return render('403.html')

def test_form_view(request):
    if request.method=="GET":
        # form = Employee_Form()
        # form = User_Form()
        # form = NameForm()
        # form = Registration_Form()
        form1 = NameForm()
        form2 = NameForm()
        context={'form1':form1, 'form2':form2}
        return render(request, 'test_form.html', context)
    elif request.method=="POST":
        print(request.POST)

def test_view(request):
    # NameFormSet = formset_factory(NameForm, extra=4)
    print(request.method)
    if request.method == "GET":
        form = NameForm()
        context = {'form':form}
        return render(request, 'test_form.html', context)
    elif request.method == "POST":
        pass
    elif request.method == "PATCH":
        new_data = json.loads(request.body)

