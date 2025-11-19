import random
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings

def generate_verification_code():
    return str(random.randint(10000, 99999))

def send_verification_email(user, subject, message_template):
    code = generate_verification_code()
    
    user.verification_code = code
    user.code_expires_at = timezone.now() + timedelta(minutes=15)
    user.save()

    message = message_template.format(code=code)
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )
    return code
