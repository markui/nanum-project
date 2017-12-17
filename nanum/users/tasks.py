from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail


@shared_task(name='send_password_reset_email')
def send_password_reset_email(email, html_content, text_content):
    send_mail('비밀번호 재설정',
              text_content,
              settings.EMAIL_MAIN,
              [email],
              html_message=html_content,
              fail_silently=False,
              )
    print(f'{email}로 이메일을 전송중입니다..')
