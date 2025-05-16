import json
import os
from django.core.management.base import BaseCommand
from django.core.files import File
from plantapp.models import Plant, ShoppingItem


class Command(BaseCommand):
    help = 'Imports plant data from JSON file'

    def handle(self, *args, **options):
        data_file = os.path.join(os.path.dirname(__file__), 'plants_data.json')

        if not os.path.exists(data_file):
            self.stdout.write(self.style.ERROR('plants_data.json file not found.'))
            return

        with open(data_file) as f:
            plants_data = json.load(f)

        for plant_data in plants_data:
            plant = Plant.objects.create(
                name=plant_data['name'],
                scientific_name=plant_data['scientific_name'],
                plant_type=plant_data['plant_type'],
                description=plant_data['description'],
                difficulty=plant_data['difficulty'],
                growth_rate=plant_data['growth_rate'],
                max_height=plant_data['max_height'],
                foliage_color=plant_data['foliage_color'],
                sunlight_hours=plant_data['sunlight_hours'],
                sunlight_type=plant_data['sunlight_type'],
                soil_type=plant_data['soil_type'],
                ph_min=plant_data['ph_min'],
                ph_max=plant_data['ph_max'],
                humidity_min=plant_data['humidity_min'],
                watering_level=plant_data.get('watering_level', ''),
                watering_frequency=plant_data['watering_frequency'],
                fertilizing_frequency=plant_data['fertilizing_frequency'],
                pruning_frequency=plant_data['pruning_frequency'],
                special_care_instructions=plant_data.get('special_care_instructions', ''),
                toxic_to_pets=plant_data['toxic_to_pets'],
                toxic_to_humans=plant_data['toxic_to_humans'],
            )

            # Add image (if available)
            image_path = os.path.join(os.path.dirname(__file__), 'plant_images', plant_data['image'])
            if os.path.exists(image_path):
                with open(image_path, 'rb') as img_file:
                    plant.image.save(plant_data['image'], File(img_file), save=True)
            else:
                self.stdout.write(self.style.WARNING(f"Image not found for {plant.name}: {plant_data['image']}"))

            # Add shopping items (if any)
            for item_data in plant_data.get('shopping_items', []):
                ShoppingItem.objects.create(
                    plant=plant,
                    name=item_data['name'],
                    description=item_data['description'],
                    affiliate_link=item_data['affiliate_link'],
                    price=item_data['price'],
                )

        self.stdout.write(self.style.SUCCESS('Successfully imported plant data.'))
