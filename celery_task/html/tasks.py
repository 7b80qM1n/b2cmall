from celery_task.celery import app
import os


@app.task(name="get_categories_static")
def get_categories_static():
    """商品频道数据静态化"""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "B2cMall.settings.dev")
    import django
    django.setup()
    from utils.crons import get_categories_context, generate_static_html
    categories = get_categories_context()

    context = {
        'categories': categories
    }

    generate_static_html(context, template_name='list.html', name_html='list.html')
    return True

@app.task(name="get_sku_detail_static")
def get_sku_detail_static(sku_id):
    """商品详情静态化"""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "B2cMall.settings.dev")
    import django
    django.setup()
    from utils.crons import get_categories_context, get_sku_detail_context, generate_static_html
    categories = get_categories_context()
    sku, goods, specs = get_sku_detail_context(sku_id)
    context = {
        'categories': categories,
        'sku': sku,
        'goods': goods,
        'specs': specs,
    }

    generate_static_html(context, template_name='detail.html', name_html=f'goods/{str(sku_id)}.html')
    return True
