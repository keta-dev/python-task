from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect, render
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from .models import Task
from django import forms

# Create your views here.
class TaskForm(forms.ModelForm):
  class Meta:
    model = Task
    fields = ['title', 'description', 'completed']

def is_admin(user):
  return user.is_superuser or user.is_staff

@login_required
def task_create(request):
  if request.method == 'POST':
    form = TaskForm(request.POST)
    if form.is_valid():
      # create task but don't save the database yet
      task = form.save(commit=False)
      # assign the current user to the task
      task.user = request.user
      # now save to database
      task.save()
      return redirect('task_list')
  else:
    form = TaskForm()
  return render(request, 'tasks/task_form.html', {'form': form})

@login_required
def task_list(request):
  if is_admin(request.user):
    tasks = Task.objects.all()
    is_admin_view = True
  else:
    tasks = Task.objects.filter(user=request.user)
    is_admin_view = False
  return render(request, 'tasks/task_list.html', {
    'tasks': tasks,
    'is_admin': is_admin_view
  })

@login_required
def task_update(request, id):
  if is_admin(request.user):
    task = get_object_or_404(Task, id=id)
  else:
    task = get_object_or_404(Task, id=id, user=request.user)


  if request.method == 'POST':
    form = TaskForm(request.POST, instance=task)
    if form.is_valid():
      form.save()
      return redirect('task_list')
  else:
    form = TaskForm(instance=task)
  return render(request, 'tasks/task_form.html', {'form': form})

@login_required
def task_delete(request, id):
  if is_admin(request.user):
    task = get_object_or_404(Task, id=id)
  else:
    task = get_object_or_404(Task, id=id, user=request.user)
    
  task.delete()
  return redirect('task_list')

# REGISTER VIEW
def register(request):
  if request.method == 'POST':
    form = UserCreationForm(request.POST)
    if form.is_valid():
      form.save()
      return redirect("login")
  else:
    form = UserCreationForm()
  return render(request, "tasks/register.html",{"form":form})

# LOGIN VIEW
def user_login(request):
  if request.method == 'POST':
    form = AuthenticationForm(request, data=request.POST)
    if form.is_valid():
      user = form.get_user()
      login(request, user)
      return redirect("task_list")
  else:
    form = AuthenticationForm()
  return render(request, 'tasks/login.html', {"form":form})

# LOGOUT VIEW
def user_logout(request):
  logout(request)
  return redirect("login")