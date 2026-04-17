from django.db import models
from django.utils.translation import gettext_lazy as _


class Brand(models.Model):
    name = models.CharField(_("name"), max_length=100, unique=True)
    slug = models.SlugField(_("slug"), max_length=120, unique=True)

    class Meta:
        verbose_name = _("brand")
        verbose_name_plural = _("brands")
        ordering = ["name"]

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(_("name"), max_length=100, unique=True)
    slug = models.SlugField(_("slug"), max_length=120, unique=True)

    class Meta:
        verbose_name = _("category")
        verbose_name_plural = _("categories")
        ordering = ["name"]

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(_("name"), max_length=100, unique=True)
    slug = models.SlugField(_("slug"), max_length=120, unique=True)

    class Meta:
        verbose_name = _("tag")
        verbose_name_plural = _("tags")
        ordering = ["name"]

    def __str__(self):
        return self.name


class Product(models.Model):
    item_code = models.CharField(
        _("item code"), max_length=100, unique=True, db_index=True
    )
    name_ar = models.CharField(_("Arabic name"), max_length=255)
    name_en = models.CharField(_("English name"), max_length=255, blank=True)

    brand = models.ForeignKey(
        Brand,
        on_delete=models.PROTECT,
        related_name="products",
        verbose_name=_("brand"),
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products",
        verbose_name=_("category"),
    )
    tags = models.ManyToManyField(Tag, blank=True, verbose_name=_("tags"))

    image = models.ImageField(_("image"), upload_to="products/", blank=True)

    pieces_per_package = models.PositiveIntegerField(
        _("pieces per package"), default=1
    )
    packages_per_carton = models.PositiveIntegerField(
        _("packages per carton"), default=1
    )

    wholesale_price = models.DecimalField(
        _("wholesale price"), max_digits=10, decimal_places=2, null=True, blank=True
    )

    qty_building_warehouse = models.IntegerField(
        _("qty — building warehouse"), default=0
    )
    qty_sea_warehouse = models.IntegerField(
        _("qty — sea warehouse"), default=0
    )
    qty_shop = models.IntegerField(_("qty — shop"), default=0)

    class Meta:
        verbose_name = _("product")
        verbose_name_plural = _("products")
        ordering = ["item_code"]

    def __str__(self):
        return f"{self.item_code} — {self.name_ar}"

    @property
    def total_qty(self):
        return self.qty_building_warehouse + self.qty_sea_warehouse + self.qty_shop

    @property
    def pieces_per_carton(self):
        return self.pieces_per_package * self.packages_per_carton
