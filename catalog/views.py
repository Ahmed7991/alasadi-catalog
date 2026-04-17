from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import render

from .models import Brand, Category, Product


PAGE_SIZE = 24
HOME_CATEGORY_LIMIT = 8


def home(request):
    """Landing page: hero, popular categories, features."""
    categories = (
        Category.objects
        .annotate(product_count=Count("products"))
        .filter(product_count__gt=0)
        .order_by("-product_count", "name")[:HOME_CATEGORY_LIMIT]
    )
    return render(request, "catalog/home.html", {"categories": categories})


def product_list(request):
    products = Product.objects.select_related("brand", "category").all()

    category_id = request.GET.get("category") or ""
    brand_id = request.GET.get("brand") or ""
    q = (request.GET.get("q") or "").strip()

    if category_id:
        products = products.filter(category_id=category_id)
    if brand_id:
        products = products.filter(brand_id=brand_id)
    if q:
        products = products.filter(
            Q(name_ar__icontains=q)
            | Q(name_en__icontains=q)
            | Q(item_code__icontains=q)
        )

    paginator = Paginator(products, PAGE_SIZE)
    page_obj = paginator.get_page(request.GET.get("page"))

    # Query string (without the `page` key) for pagination links to preserve filters.
    qs_params = request.GET.copy()
    qs_params.pop("page", None)
    base_querystring = qs_params.urlencode()

    context = {
        "page_obj": page_obj,
        "products": page_obj.object_list,
        "categories": Category.objects.all(),
        "brands": Brand.objects.all(),
        "selected_category": category_id,
        "selected_brand": brand_id,
        "q": q,
        "base_querystring": base_querystring,
    }
    return render(request, "catalog/product_list.html", context)
