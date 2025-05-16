from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Plant, UserPlant, CareTask, ShoppingItem
from .forms import PlantSearchForm, UserPlantForm, CareTaskForm
from django.core.paginator import Paginator
from datetime import date, timedelta
from .utils import recommend_plants
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # Or wherever you want to redirect
    else:
        form = UserCreationForm()
    
    return render(request, 'registration/register.html', {'form': form})



def home(request):
    featured_plants = Plant.objects.all().order_by('?')[:6]
    return render(request, 'plantapp/home.html', {'featured_plants': featured_plants})

def plant_list(request):
    form = PlantSearchForm(request.GET or None)
    plants = Plant.objects.all()
    
    if form.is_valid():
        plant_type = form.cleaned_data.get('plant_type')
        difficulty = form.cleaned_data.get('difficulty')
        sunlight_hours = form.cleaned_data.get('sunlight_hours')
        sunlight_type = form.cleaned_data.get('sunlight_type')
        min_temperature = form.cleaned_data.get('min_temperature')
        max_temperature = form.cleaned_data.get('max_temperature')
        flower_color = form.cleaned_data.get('flower_color')
        toxic_to_pets = form.cleaned_data.get('toxic_to_pets')
        
        if plant_type:
            plants = plants.filter(plant_type=plant_type)
        if difficulty:
            plants = plants.filter(difficulty=difficulty)
        if sunlight_hours:
            plants = plants.filter(sunlight_hours__lte=sunlight_hours)
        if sunlight_type:
            plants = plants.filter(sunlight_type=sunlight_type)
        if min_temperature:
            plants = plants.filter(min_temperature__gte=min_temperature)
        if max_temperature:
            plants = plants.filter(max_temperature__lte=max_temperature)
        if flower_color:
            plants = plants.filter(flower_color__icontains=flower_color)
        if toxic_to_pets is not None:
            plants = plants.filter(toxic_to_pets=not toxic_to_pets)
    if form.is_valid():
        user_input = form.cleaned_data
        plants = recommend_plants(user_input)
    else:
        plants = Plant.objects.all()


    # Pagination
    paginator = Paginator(plants, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'plantapp/plant_list.html', {
        'form': form,
        'page_obj': page_obj,
    })

def plant_detail(request, pk):
    plant = get_object_or_404(Plant, pk=pk)
    related_items = ShoppingItem.objects.filter(plant=plant)[:4]
    return render(request, 'plantapp/plant_detail.html', {
        'plant': plant,
        'related_items': related_items,
    })

@login_required
def add_user_plant(request, plant_id):
    plant = get_object_or_404(Plant, pk=plant_id)
    if request.method == 'POST':
        form = UserPlantForm(request.POST)
        if form.is_valid():
            user_plant = form.save(commit=False)
            user_plant.user = request.user
            user_plant.plant = plant
            user_plant.save()
            
            # Create initial care tasks
            CareTask.objects.create(
                user_plant=user_plant,
                task_type='water',
                due_date=date.today() + timedelta(days=plant.watering_frequency)
            )
            
            messages.success(request, f"{plant.name} has been added to your collection!")
            return redirect('my_plants')
    else:
        form = UserPlantForm()
    
    return render(request, 'plantapp/add_user_plant.html', {'form': form, 'plant': plant})

@login_required
def my_plants(request):
    plants = UserPlant.objects.filter(user=request.user)
    return render(request, 'plantapp/my_plants.html', {'plants': plants})

@login_required
def plant_care(request, user_plant_id):
    user_plant = get_object_or_404(UserPlant, pk=user_plant_id, user=request.user)
    tasks = CareTask.objects.filter(user_plant=user_plant).order_by('due_date')
    
    if request.method == 'POST':
        form = CareTaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user_plant = user_plant
            task.save()
            messages.success(request, 'Task added successfully!')
            return redirect('plant_care', user_plant_id=user_plant.id)
    else:
        form = CareTaskForm()
    
    return render(request, 'plantapp/plant_care.html', {
        'user_plant': user_plant,
        'tasks': tasks,
        'form': form,
    })

@login_required
def complete_task(request, task_id):
    task = get_object_or_404(CareTask, pk=task_id, user_plant__user=request.user)
    task.completed = True
    task.completed_date = date.today()
    task.save()
    
    # Reschedule recurring tasks
    if task.task_type == 'water':
        new_due_date = date.today() + timedelta(days=task.user_plant.plant.watering_frequency)
        CareTask.objects.create(
            user_plant=task.user_plant,
            task_type='water',
            due_date=new_due_date
        )
    
    messages.success(request, 'Task marked as complete!')
    return redirect('plant_care', user_plant_id=task.user_plant.id)

@login_required
def care_calendar(request):
    tasks = CareTask.objects.filter(
        user_plant__user=request.user,
        completed=False,
        due_date__gte=date.today()
    ).order_by('due_date')
    
    return render(request, 'plantapp/care_calendar.html', {'tasks': tasks})

def shopping(request):
    items = ShoppingItem.objects.all()
    return render(request, 'plantapp/shopping.html', {'items': items})