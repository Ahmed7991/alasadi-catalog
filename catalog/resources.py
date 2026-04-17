from django.utils.text import slugify
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget

from .models import Brand, Category, Product


class ProductResource(resources.ModelResource):
    brand = fields.Field(
        column_name="brand",
        attribute="brand",
        widget=ForeignKeyWidget(Brand, field="name"),
    )
    category = fields.Field(
        column_name="category",
        attribute="category",
        widget=ForeignKeyWidget(Category, field="name"),
    )

    class Meta:
        model = Product
        import_id_fields = ("item_code",)
        skip_unchanged = True
        use_bulk = True
        fields = (
            "item_code",
            "name_ar",
            "name_en",
            "brand",
            "category",
            "wholesale_price",
            "pieces_per_package",
            "packages_per_carton",
            "qty_building_warehouse",
            "qty_sea_warehouse",
            "qty_shop",
        )

    def _get_or_create_slug(self, name: str) -> str:
        slug = slugify(name, allow_unicode=True)
        return slug if slug else name.replace(" ", "-")

    def before_import_row(self, row, **kwargs):
        brand_name = (row.get("brand") or "").strip()
        row["brand"] = brand_name
        Brand.objects.get_or_create(
            name=brand_name,
            defaults={"slug": self._get_or_create_slug(brand_name)},
        )

        category_name = (row.get("category") or "").strip()
        row["category"] = category_name
        Category.objects.get_or_create(
            name=category_name,
            defaults={"slug": self._get_or_create_slug(category_name)},
        )
