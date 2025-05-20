from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
from django.views.generic import ListView
from django.contrib.auth.forms import UserCreationForm

from datetime import date, timedelta
import re

from .models import Plant, UserPlant, CareTask, ShoppingItem, Product
from .forms import PlantSearchForm, UserPlantForm, CareTaskForm, PlantImageUploadForm
from .utils import recommend_plants


def parse_watering_frequency(frequency_str):
    """Convert strings like 'Every 2 weeks' to number of days."""
    match = re.search(r'Every (\d+) (day|week|month)', frequency_str)
    if match:
        num = int(match.group(1))
        unit = match.group(2)
        if unit == 'day':
            return num
        elif unit == 'week':
            return num * 7
        elif unit == 'month':
            return num * 30  # Approximate
    return 7  # Default fallback


def home(request):
    featured_plants = Plant.objects.all().order_by('?')[:6]
    return render(request, 'plantapp/home.html', {'featured_plants': featured_plants})


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


class PlantListView(ListView):
    model = Plant
    template_name = 'plant_list.html'
    context_object_name = 'plants'
    paginate_by = 10


def plant_list(request):
    form = PlantSearchForm(request.GET or None)
    plants = Plant.objects.all().order_by('id')

    if form.is_valid():
        # You can choose to filter with individual fields or use recommendation
        user_input = form.cleaned_data
        
        # Basic filtering
        if user_input.get('plant_type'):
            plants = plants.filter(plant_type=user_input['plant_type'])
        if user_input.get('difficulty'):
            plants = plants.filter(difficulty=user_input['difficulty'])
        if user_input.get('sunlight_hours'):
            plants = plants.filter(sunlight_hours__lte=user_input['sunlight_hours'])
        if user_input.get('sunlight_type'):
            plants = plants.filter(sunlight_type=user_input['sunlight_type'])
        if user_input.get('min_temperature'):
            plants = plants.filter(min_temperature__gte=user_input['min_temperature'])
        if user_input.get('max_temperature'):
            plants = plants.filter(max_temperature__lte=user_input['max_temperature'])
        if user_input.get('flower_color'):
            plants = plants.filter(flower_color__icontains=user_input['flower_color'])
        if user_input.get('toxic_to_pets') is not None:
            plants = plants.filter(toxic_to_pets=not user_input['toxic_to_pets'])

        # Further refine using recommend_plants util if desired
        plants = recommend_plants(user_input)

    # Pagination
    paginator = Paginator(plants, 6)
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
                due_date=date.today() + timedelta(days=parse_watering_frequency(plant.watering_frequency))
            )

            messages.success(request, f"{plant.name} has been added to your collection!")
            return redirect('my_plants')
    else:
        form = UserPlantForm()

    return render(request, 'plantapp/add_user_plant.html', {'form': form, 'plant': plant})


@login_required
def my_plants(request):
    plants = UserPlant.objects.filter(user=request.user).select_related('plant')
    return render(request, 'plantapp/my_plants.html', {'plants': plants})


@login_required
def plant_care(request, user_plant_id):
    user_plant = get_object_or_404(UserPlant, pk=user_plant_id, user=request.user)
    tasks = CareTask.objects.filter(user_plant=user_plant).order_by('due_date')
    today = timezone.now().date()

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
        'today': today
    })


@login_required
def complete_task(request, task_id):
    task = get_object_or_404(CareTask, pk=task_id, user_plant__user=request.user)
    task.completed = True
    task.completed_date = date.today()
    task.save()

    # Reschedule recurring water tasks
    if task.task_type == 'water':
        new_due_date = date.today() + timedelta(days=parse_watering_frequency(task.user_plant.plant.watering_frequency))
        CareTask.objects.create(
            user_plant=task.user_plant,
            task_type='water',
            due_date=new_due_date
        )

    messages.success(request, 'Task marked as complete!')
    return redirect('plant_care', user_plant_id=task.user_plant.id)


@login_required
def care_calendar(request):
    today = timezone.now().date()
    next_week = today + timedelta(days=7)

    # Upcoming tasks within next week
    tasks = CareTask.objects.filter(
        user_plant__user=request.user,
        completed=False,
        due_date__lte=next_week
    ).order_by('due_date').select_related('user_plant', 'user_plant__plant')

    # Stats
    all_tasks = tasks

    water_tasks = all_tasks.filter(task_type='water')
    fertilize_tasks = all_tasks.filter(task_type='fertilize')
    prune_tasks = all_tasks.filter(task_type='prune')

    total_tasks = all_tasks.count()
    water_percent = (water_tasks.count() / total_tasks * 100) if total_tasks else 0
    fertilize_percent = (fertilize_tasks.count() / total_tasks * 100) if total_tasks else 0
    prune_percent = (prune_tasks.count() / total_tasks * 100) if total_tasks else 0

    # Recently completed tasks
    completed_tasks = CareTask.objects.filter(
        user_plant__user=request.user,
        completed=True
    ).order_by('-completed_date')[:5]

    return render(request, 'plantapp/care_calendar.html', {
        'tasks': tasks,
        'today': today,
        'water_tasks': water_tasks,
        'fertilize_tasks': fertilize_tasks,
        'prune_tasks': prune_tasks,
        'water_percent': water_percent,
        'fertilize_percent': fertilize_percent,
        'prune_percent': prune_percent,
        'completed_tasks': completed_tasks
    })


def shopping(request):
    items = Product.objects.all()
    return render(request, 'plantapp/shopping.html', {'items': items})


@login_required
def upload_plant_image(request):
    if request.method == 'POST':
        form = PlantImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('plant_image_upload')
    else:
        form = PlantImageUploadForm()
    return render(request, 'plantapp/upload_image.html', {'form': form})
