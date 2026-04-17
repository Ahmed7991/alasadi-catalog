from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from .models import Brand, Category, Tag, Product
from .resources import ProductResource


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


@admin.register(Product)
class ProductAdmin(ImportExportModelAdmin):
    resource_classes = [ProductResource]
    list_display = (
        "item_code",
        "name_ar",
        "name_en",
        "brand",
        "category",
        "wholesale_price",
        "total_qty",
    )
    search_fields = ("item_code", "name_ar", "name_en")
    list_filter = ("brand", "category", "tags")
    filter_horizontal = ("tags",)
