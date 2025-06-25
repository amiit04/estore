from django.shortcuts import render, redirect
from django.views import View
from account.models import Customer, CustomerAddress
from .models import Product, Cart, CartProduct
from shop.models import Category,Brand,Color
from products.models import Order
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts           import render, get_object_or_404
from django.urls                import reverse

class ShopView(View):
    template_name = "shop.html"
    
    def get(self,request,*args,**kwargs):
        context = {}
        category_list = Category.objects.filter(is_active=True)
        brand_list = Brand.objects.filter(is_active=True)
        color_list = Color.objects.filter(is_active=True)
        
        if (request.GET and request.GET.get('q') == "") or not request.GET:
            products = Product.objects.filter(is_active=True)
            context['product_list'] = products
        elif request.GET:
            if request.GET.get('q') is not None:
                products = Product.objects.filter(title__icontains = request.GET.get('q'))
            elif request.GET.get('category') is not None :
                products = Product.objects.filter(category__slug = request.GET['category'])
            elif request.GET.get('brand') is not None:
                products = Product.objects.filter(brand__slug = request.GET['brand'])
            elif request.GET.get('sort') is not None:
                sortp = request.GET.get('sort')
                q = ''
                if sortp == 'l_h':
                    q = 'selling_price'
                elif sortp == 'h_l':
                    q = '-selling_price'
                elif sortp == 'a_z':
                    q = 'title'
                else:
                    q = '-title'
                
                products = Product.objects.all().order_by(q)
            elif request.GET.get('color') is not None:
                products = Product.objects.filter(color__color_name = request.GET['color'])
            elif request.GET.get('srate') is not None and request.GET.get('erate') is not None:
                srate = request.GET.get('srate')
                erate = request.GET.get('erate')
                if erate == 0:
                    products = Product.objects.filter(selling_price__gt=srate)
                else:
                    products = Product.objects.filter(selling_price__gt=srate, selling_price__lt=erate)
                    
                print(products.query)
            context['product_list'] = products
            cate = products.values_list("category",flat=True).distinct()
            
            
        
            
        context['category_list'] = category_list
        context['brand_list'] = brand_list
        context['color_list'] = color_list
        return render(request,self.template_name,context)

class ShopDetailView(View):
    template_name = "shop-details.html"
    def get(self,request,*args,**kwargs):
        pslug =  kwargs['pd']
        pdetail = Product.objects.get(slug=pslug)
        context = { 'product' : pdetail }
        return render(request,self.template_name,context)
        
class CartView(View):
    template_name = "cart.html"
    def get(self,request,*args,**kwargs):
        if request.user.is_authenticated and not request.user.is_staff:
            customer =  Customer.objects.get(user_id = request.user) 
            cart_list, created = Cart.objects.get_or_create(customer=customer,defaults={'total': 0})
            return render(request,self.template_name,{'allcartprod':cart_list})
        else:
            return redirect("login")
    

class CheckoutView(LoginRequiredMixin, View):
    template_name = "home/checkout.html"

    def get(self, request, *args, **kwargs):
        customer       = get_object_or_404(Customer, user_id=request.user)
        cart           = get_object_or_404(Cart, customer=customer)
        cart_products  = CartProduct.objects.filter(cart=cart)
        if not cart_products.exists():
            return redirect("cart")

        total = sum(cp.subtotal for cp in cart_products)

        # try to fetch an existing address, or None
        try:
            customer_address = CustomerAddress.objects.get(user_id=request.user)
        except CustomerAddress.DoesNotExist:
            customer_address = None

        return render(request, self.template_name, {
            "cart_products":    cart_products,
            "total":            total,
            "customer_address": customer_address,
        })

    def post(self, request, *args, **kwargs):
        customer      = get_object_or_404(Customer, user_id=request.user)
        cart          = get_object_or_404(Cart, customer=customer)
        cart_products = CartProduct.objects.filter(cart=cart)
        if not cart_products.exists():
            return redirect("cart")

        # 1) Pull form fields
        ship_addr = request.POST["shipping_address"].strip()
        bill_addr = request.POST["billing_address"].strip()
        city      = request.POST["city"].strip()
        state     = request.POST["state"].strip()
        postal    = request.POST["postal_code"].strip()
        country   = request.POST["country"].strip()
        mobile    = request.POST["mobile"].strip()

        # 2) Create or update the one-to-one CustomerAddress
        customer_address, created = CustomerAddress.objects.update_or_create(
            user_id = request.user,
            defaults = {
                "shipping_address": ship_addr,
                "billing_address":  bill_addr,
                "city":             city,
                "state":            state,
                "postal_code":      postal,
                "country":          country,
                "default":          True,
                "is_active":        True,
            }
        )

        # 3) Compute totals
        subtotal = sum(cp.subtotal for cp in cart_products)
        discount = 0  # your discount logic
        total    = subtotal - discount

        # 4) Create the Order, linking the new CustomerAddress
        order = Order.objects.create(
            cart              = cart,
            ordered_by        = request.user,
            shipping_address  = customer_address,
            billing_address   = customer_address,
            mobile            = mobile,
            subtotal          = subtotal,
            discount          = discount,
            total             = total,
            order_status      = "Order Received",
        )

        # 5) Clear the cart
        cart_products.delete()
        cart.delete()

        return redirect(reverse("order_detail", args=[order.id]))

class OrderDetailView(LoginRequiredMixin, View):
    template_name = "home/order_detail.html"

    def get(self, request, order_id, *args, **kwargs):
        order = get_object_or_404(Order, id=order_id, ordered_by=request.user)
        cart_products = order.cart.cartproduct.all()
        return render(request, self.template_name, {'order': order,'cart_products': cart_products,})