from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Plant(models.Model):
    # Choice fields
    INDOOR = 'indoor'
    OUTDOOR = 'outdoor'
    PLANT_TYPE_CHOICES = [
        (INDOOR, 'Indoor'),
        (OUTDOOR, 'Outdoor'),
    ]

    EASY = 'easy'
    MEDIUM = 'medium'
    HARD = 'hard'
    DIFFICULTY_CHOICES = [
        (EASY, 'Easy'),
        (MEDIUM, 'Medium'),
        (HARD, 'Hard'),
    ]

    LOW = 'low'
    MODERATE = 'moderate'
    HIGH = 'high'
    WATERING_LEVEL_CHOICES = [
        (LOW, 'Low'),
        (MODERATE, 'Moderate'),
        (HIGH, 'High'),
    ]

    # Basic info
    name = models.CharField(max_length=100)
    scientific_name = models.CharField(max_length=100)
    plant_type = models.CharField(max_length=10, choices=PLANT_TYPE_CHOICES)
    description = models.TextField()
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES)
    growth_rate = models.CharField(max_length=50)
    max_height = models.CharField(max_length=50)
    foliage_color = models.CharField(max_length=50)
    image = models.ImageField(upload_to='plant_images/', blank=True)
    thumbnail = models.ImageField(upload_to='plant_thumbnails/', blank=True)

    # Environmental requirements
    sunlight_hours = models.IntegerField()
    sunlight_type = models.CharField(max_length=50)  # direct, indirect, shade
    soil_type = models.CharField(max_length=50)
    ph_min = models.DecimalField(max_digits=3, decimal_places=1)
    ph_max = models.DecimalField(max_digits=3, decimal_places=1)
    humidity_min = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])

    # Watering
    watering_level = models.CharField(max_length=10, choices=WATERING_LEVEL_CHOICES)
    watering_frequency_days = models.IntegerField(
        help_text="Number of days between waterings",
        default=7
    )

    def get_watering_frequency_display(self):
        """Convert watering_frequency_days to human-readable format"""
        if self.watering_frequency_days % 7 == 0:
            weeks = self.watering_frequency_days // 7
            return f"Every {weeks} week{'s' if weeks > 1 else ''}"
        return f"Every {self.watering_frequency_days} day{'s' if self.watering_frequency_days > 1 else ''}"

    # Care
    fertilizing_frequency = models.CharField(max_length=50)
    pruning_frequency = models.CharField(max_length=50)
    special_care_instructions = models.TextField(blank=True)

    # Toxicity
    toxic_to_pets = models.BooleanField(default=False)
    toxic_to_humans = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class UserPlant(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plant = models.ForeignKey(Plant, on_delete=models.CASCADE)
    date_added = models.DateField(auto_now_add=True)
    nickname = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=100)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.username}'s {self.plant.name}"


class CareTask(models.Model):
    WATER = 'water'
    FERTILIZE = 'fertilize'
    PRUNE = 'prune'
    REPOT = 'repot'
    CHECK = 'check'
    TASK_TYPE_CHOICES = [
        (WATER, 'Water'),
        (FERTILIZE, 'Fertilize'),
        (PRUNE, 'Prune'),
        (REPOT, 'Repot'),
        (CHECK, 'Check for pests'),
    ]

    user_plant = models.ForeignKey(UserPlant, on_delete=models.CASCADE)
    task_type = models.CharField(max_length=10, choices=TASK_TYPE_CHOICES)
    due_date = models.DateField()
    completed = models.BooleanField(default=False)
    completed_date = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.task_type} for {self.user_plant}"


class ShoppingItem(models.Model):
    plant = models.ForeignKey(Plant, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()
    affiliate_link = models.URLField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.ImageField(upload_to='shopping_images/', blank=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    affiliate_link = models.URLField()

    def __str__(self):
        return self.name
