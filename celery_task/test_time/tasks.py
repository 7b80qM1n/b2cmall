from celery_task.celery import app
import os


@app.task
def get_index_static():
    """首页(商品频道数据+广告数据)静态化"""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "B2cMall.settings.dev")
    import django
    django.setup()
    from utils.crons import get_categories_context, get_contents_context, generate_static_html

    categories = get_categories_context()
    contents = get_contents_context()

    context = {
        'categories': categories,
        'contents': contents
    }
    generate_static_html(context, template_name='index.html', name_html='index.html')
    return True
