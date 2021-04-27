from celery_task.celery import app
from django.core.mail import send_mail


@app.task(name="send_verify_email")
def send_verify_email(to_email, verify_url):
    import os
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "B2cMall.settings.dev")
    import django
    from django.conf import settings
    django.setup()
    subject = '邮件激活-7b80qM1n'
    html_message = f'<p>亲爱的{to_email}</p>' \
                   '<br>' \
                   '<p>感谢您注册.请点击此链接激活您的邮箱:</p>' \
                   f'<p><a href="{verify_url}">{verify_url}</a></p>' \
                   '<br>'\
                   '<p>(这是一封自动生成的email,请勿回复)</p>'

    send_mail(subject, '', settings.DEFAULT_FROM_EMAIL, [to_email, ], html_message=html_message)
