from django.contrib import admin
from .models import GoodsCategory, GoodsChannel, Brand, Goods, GoodsSpecification, SpecificationOption, SKU, SKUImage, SKUSpecification
from celery_task.html.tasks import get_categories_static, get_sku_detail_static

class GoodsCategoryAdmin(admin.ModelAdmin):

    def save_model(self, request, obj, form, change):
        """
        admin点击保存按钮会调用此方法
        """
        obj.save()
        # 重新生成新的列表静态界面
        get_categories_static.delay()

    def delete_model(self, request, obj):
        """
        admin点击删除按钮会调用此方法
        """
        obj.delete()
        # 重新生成新的列表静态界面
        get_categories_static.delay()

class SKUAdmin(admin.ModelAdmin):

    def save_model(self, request, obj, form, change):
        """
        admin点击保存按钮会调用此方法
        """
        obj.save()
        # 重新生成新的列表静态界面
        get_sku_detail_static.delay(obj.id)

class SKUImageAdmin(admin.ModelAdmin):

    def save_model(self, request, obj, form, change):
        """
        admin点击保存按钮会调用此方法
        """
        obj.save()

        sku = obj.sku
        if not sku.default_image_url:
            sku.default_image_url = obj
        # 重新生成新的列表静态界面
        get_sku_detail_static.delay(sku.id)

    def delete_model(self, request, obj):
        """
        admin点击删除按钮会调用此方法
        """
        obj.delete()
        sku = obj.sku
        # 重新生成新的列表静态界面
        get_sku_detail_static.delay(sku.id)


admin.site.register(GoodsCategory, GoodsCategoryAdmin)
admin.site.register(GoodsChannel)
admin.site.register(Brand)
admin.site.register(Goods)
admin.site.register(GoodsSpecification)
admin.site.register(SpecificationOption)
admin.site.register(SKU, SKUAdmin)
admin.site.register(SKUImage, SKUImageAdmin)
admin.site.register(SKUSpecification)

