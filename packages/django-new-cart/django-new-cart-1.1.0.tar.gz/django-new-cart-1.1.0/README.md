[![StandWithUkraine](https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/badges/StandWithUkraine.svg)](https://github.com/vshymanskyy/StandWithUkraine/blob/main/docs/README.md)
[![Stand With Ukraine](https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/banner2-direct.svg)](https://vshymanskyy.github.io/StandWithUkraine/)
# NOTICE
This frameworks is a fork of another with the same name... Some improvement were made with the target in mind that increase the capabilities of the django-cart
# INSTALATION
```
pip3 install django-new-cart
``` 
# USAGE
The target of this module is to allow programmers to handle easily the cart of his/her shop web app...
## Update urls.py with this url
```python
urlpatterns += [ 
    path("cart/add/<id>/", add, name="cart_add"),
    path("cart/add/<id>/<quantity>/", add_quant, name="cart_add_quantity"),
    path("cart/remove/<id>/", remove, name="cart_remove"),
    path("cart/remove/<id>/<quantity>/", remove_quant, name="cart_remove_quantity"),
    path("cart/clear/", cart_clear, name="cart_clear"),
    path("cart/pop/", cart_pop, name="cart_pop"),
    path("cart/clear/<id>/", item_clear, name="cart_clear_id"),
    path("cart/details/<id>/", cart_detail, name="cart_details"),
    path("cart/update/", update_cart, name="cart_update"),
]
```

## Adding an element
```python
@require_POST
def add(request: HttpRequest, id: int):
    cart = Cart(request)
    cart.add(product=Products.objects.filter(id=id).first())
    return JsonResponse({"result": "ok", 
        "amount": cart.session[CART_SESSION_ID].get(id, {"quantity": 0})["quantity"]
    }
```

## Get details of the cart
```python
@require_POST
def cart_detail(request:HttpRequest, id: int):
    return JsonResponse({"result": Cart(request).get_item(id)})
```

## Cleaning the cart
```python
@require_POST
def cart_clear(request:HttpRequest):
    Cart(request).clear()
    return JsonResponse({"result": "ok", "amount": 0})
```

## Remove all elements of a type from cart
```python
@require_POST
def item_clear(request: HttpRequest, id:int):
    cart = Cart(request)
    cart.remove(product=Products.objects.filter(id=id).first())
    return JsonResponse({
        "result": "ok", 
        "amount": cart.get_sum_of("quantity") 
    })
```

## Removing N elements from cart
```python
@require_POST
def remove_quant(request:HttpRequest, id:int, quantity: int):
    Cart(request).add(product=Products.objects.filter(id=id).first(), quantity=quantity, action="remove")
    return JsonResponse({"result": "ok"})
```

## Remove element 
```python
@require_POST
def remove(request:HttpRequest, id: int):
    Cart(request).decrement(product=Products.objects.filter(id=id).first())
    return JsonResponse({"result": "ok"})
```

## Pop last element
```python
@require_POST
def cart_pop(request:HttpRequest,):
    cart = Cart(request)
    cart.pop()
    return JsonResponse({"result": "ok",
        "amount": cart.get_sum_of("quantity")
    })
```

## Adding N elements to cart
```python
@require_POST
def add_quant(request:HttpRequest, id:int, quantity: int):
    cart = Cart(request)
    cart.add(Producsts.objects.filter(id=id).first(), quantity)
    return JsonResponse({"result": "ok", 
        "amount": cart.session[CART_SESSION_ID].get(id, {"quantity": quantity})["quantity"]})
```
