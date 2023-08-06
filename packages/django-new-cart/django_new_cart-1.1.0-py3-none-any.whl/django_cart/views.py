from django.shortcuts import render
from django.views.decorators.http import require_POST
from django.http.request import HttpRequest
from django.http.response import HttpResponse, JsonResponse
from .apps import SingleCart, MultiCart
from clients.models import Product

# Create your views here.
@require_POST
def cart_single_add(request: HttpRequest, *args, **kwargs):
    product = Product.objects.get(id=kwargs.get("id", None))
    cart = SingleCart(request).add(
        product=product,
        quantity=request.POST.get("quantity", 1),
        custom_product_id=getattr(product, "id", None))
    return JsonResponse({
        "total": cart.cart.get_total_prod_of("quantity", request.POST.get("price_field", "price")),
        "cart": cart.car.get(str(kwargs.get("id", None)))
    })

@require_POST
def cart_multi_add(request: HttpRequest, *args, **kwargs):
    cart = MultiCart(request).add(cart_id=kwargs.get("cart_id", 0), 
        product=Product.objects.get(id=kwargs.get("id", None)),
        quantity=request.POST.get("quantity", 1), 
        custom_product_id=request.POST.get("custom_product_id", None))
    return JsonResponse({
        "total": cart.cart.get_total_prod_of("quantity", request.POST.get("price_field", "price")),
        "cart": cart.cart.get(str(kwargs.get("cart_id", 0))).get(str(kwargs.get("id", None)))
    })

@require_POST
def cart_single_clear(request: HttpRequest, *args, **kwargs):
    cart = SingleCart(request).clear()
    return JsonResponse({
        "total": cart.cart.get_total_prod_of("quantity", request.POST.get("price_field", "price")),
        "cart": cart.cart
    })

@require_POST
def cart_multi_clear(request: HttpRequest, *args, **kwargs):
    cart = MultiCart(request).clear()
    return JsonResponse({
        "total": cart.cart.get_total_prod_of("quantity", request.POST.get("price_field", "price")),
        "cart": cart.cart
    })

@require_POST
def cart_single_add_to(request: HttpRequest, *args, **kwargs):
    cart = SingleCart(request).add_to(product_id=kwargs.get("id"), 
        product=Product.objects.get(id=kwargs.get("id")),
        quantity=request.POST.get("quantity", 1))
    return JsonResponse({
        "total": cart.cart.get_total_prod_of("quantity", request.POST.get("price_field", "price")),
        "cart": cart.cart.get(str(kwargs.get("id", None)))
    })

@require_POST
def cart_multi_add_to(request: HttpRequest, *args, **kwargs):
    cart = MultiCart(request).add_to(cart_id=kwargs.get("cart_id", 0), product_id=kwargs["id"], 
        product=Product.objects.get(id=kwargs.get("id")),
        quantity=request.POST.get("quantity", 1))
    return JsonResponse({
        "total": cart.cart.get_total_prod_of("quantity", request.POST.get("price_field", "price")),
        "cart": cart.cart.get(str(kwargs.get("cart_id", 0))).get(str(kwargs.get("id", None)))
    })

@require_POST
def cart_single_sub_to(request: HttpRequest, *args, **kwargs):
    cart = SingleCart(request).decrease_from(product_id=kwargs.get("id"), 
        product=Product.objects.get(id=kwargs.get("id")),
        quantity=request.POST.get("quantity", 1))
    return JsonResponse({
        "total": cart.cart.get_total_prod_of("quantity", request.POST.get("price_field", "price")),
        "cart": cart.cart.get(str(kwargs.get("id", None)))
    })

@require_POST
def cart_multi_sub_to(request: HttpRequest, *args, **kwargs):
    cart = MultiCart(request).decrease_from(cart_id=kwargs.get("cart_id", 0), 
        product_id=kwargs.get("id"), 
        product=Product.objects.get(id=kwargs.get("id")),
        quantity=request.POST.get("quantity", 1))
    return JsonResponse({
        "total": cart.cart.get_total_prod_of("quantity", request.POST.get("price_field", "price")),
        "cart": cart.cart.get(str(kwargs.get("cart_id", 0))).get(str(kwargs.get("id", None)))
    })

@require_POST
def cart_single_del(request: HttpRequest, *args, **kwargs):
    cart = SingleCart(request).clear_product(product_id=kwargs.get("id"))
    return JsonResponse({
        "total": cart.cart.get_total_prod_of("quantity", request.POST.get("price_field", "price")),
        "cart": cart.cart
    })

@require_POST
def cart_multi_del(request: HttpRequest, *args, **kwargs):
    cart = MultiCart(request).clear_product(cart_id=kwargs.get("cart_id", 0), 
        product_id=kwargs.get("id"))
    return JsonResponse({
        "total": cart.cart.get_total_prod_of("quantity", request.POST.get("price_field", "price")),
        "cart": cart.cart
    })
