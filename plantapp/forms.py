from django import forms
from .models import Plant, UserPlant, CareTask
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Fieldset

class PlantSearchForm(forms.Form):
    PLANT_TYPE_CHOICES = [
        ('', 'Any'),
        ('indoor', 'Indoor'),
        ('outdoor', 'Outdoor'),
    ]
    
    DIFFICULTY_CHOICES = [
        ('', 'Any'),
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    
    WATERING_LEVEL_CHOICES = [
        ('', 'Any'),
        ('low', 'Low'),
        ('moderate', 'Moderate'),
        ('high', 'High'),
    ]
    
    plant_type = forms.ChoiceField(choices=PLANT_TYPE_CHOICES, required=False)
    difficulty = forms.ChoiceField(choices=DIFFICULTY_CHOICES, required=False)
    sunlight_hours = forms.IntegerField(label='Minimum sunlight hours', required=False, min_value=0, max_value=24)
    sunlight_type = forms.ChoiceField(
        choices=[
            ('', 'Any'),
            ('direct', 'Direct'),
            ('indirect', 'Indirect'),
            ('shade', 'Shade'),
        ],
        required=False
    )
    watering_level = forms.ChoiceField(choices=WATERING_LEVEL_CHOICES, required=False)
    toxic_to_pets = forms.BooleanField(label='Pet safe', required=False)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Find your perfect plant',
                Row(
                    Column('plant_type', css_class='col-md-6'),
                    Column('difficulty', css_class='col-md-6'),
                ),
                Row(
                    Column('sunlight_hours', css_class='col-md-4'),
                    Column('sunlight_type', css_class='col-md-4'),
                    Column('toxic_to_pets', css_class='col-md-4'),
                ),
                'watering_level',
                Submit('submit', 'Search Plants', css_class='btn-primary')
            )
        )

class UserPlantForm(forms.ModelForm):
    class Meta:
        model = UserPlant
        fields = ['nickname', 'location', 'notes']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Save Plant'))

class CareTaskForm(forms.ModelForm):
    class Meta:
        model = CareTask
        fields = ['task_type', 'due_date', 'notes']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Add Task'))

# added now
class PlantImageUploadForm(forms.ModelForm):
    class Meta:
        model = Plant
        fields = ['name', 'scientific_name', 'image']