from django.core.management.base import BaseCommand
from django.utils import timezone
from plantapp.models import CareTask
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Sends plant care reminders to users'
    
    def handle(self, *args, **options):
        # Get tasks due today or overdue
        tasks = CareTask.objects.filter(
            completed=False,
            due_date__lte=timezone.now().date() + timezone.timedelta(days=1)
        ).select_related('user_plant__user', 'user_plant__plant')
        
        # Group tasks by user
        user_tasks = {}
        for task in tasks:
            user_id = task.user_plant.user.id
            if user_id not in user_tasks:
                user_tasks[user_id] = []
            user_tasks[user_id].append(task)
        
        # Send emails
        for user_id, tasks in user_tasks.items():
            user = User.objects.get(id=user_id)
            subject = f"PlantSage Reminder: You have {len(tasks)} care tasks due"
            
            message = render_to_string('plantapp/emails/reminder_email.html', {
                'user': user,
                'tasks': tasks,
            })
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                html_message=message,
                fail_silently=True
            )
            
            self.stdout.write(self.style.SUCCESS(f"Sent reminder to {user.email}"))