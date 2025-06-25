from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views import View
from account.models import Customer
from site_settings.models import HomeBanner
from products.models import Cart,CartProduct,Product
from shop.models import Category
from shop.forms import ContactForm
from django.contrib.messages import add_message
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required

class HomeView(View):
    template_name = 'home/index.html'
    def get(self,request,*args,**kwargs):
        homebanner = HomeBanner.objects.filter(is_active=True)
        allcategory = Category.objects.filter(is_active=True)
        context = { 'homebanner':homebanner, 'allcategory': allcategory}
        return render(request,self.template_name,context)
    
class AboutView(View):
    template_name = 'home/about.html'
    def get(self,request,*args,**kwargs):
        return render(request,self.template_name)
    
class ContactView(View):
    template_name = 'home/contact.html'
    def get(self,request,*args,**kwargs):
        cnform = ContactForm()
        return render(request,self.template_name,{'form':cnform})
    
    def post(self,request,*args,**kwargs):
        cnform = ContactForm(request.POST)
        if cnform.is_valid():
            cnform.save()
            return redirect("contact")
        return render(request,self.template_name,{'form':cnform})

class AjaxView(View):
    def post(self,request,*args,**kwargs):
        if request.user.is_authenticated and not request.user.is_staff:
            if request.POST.get('prod_id'):
                prod_id = request.POST.get('prod_id')
                product_obj = Product.objects.get(id=prod_id)
                customer = Customer.objects.get(user_id=request.user)
                cart_obj = Cart.objects.get(customer=customer)
                if cart_obj:
                    prod_in_cart = cart_obj.cartproduct.filter(product=product_obj)
                    if prod_in_cart.exists():
                        cartproduct = prod_in_cart.last()
                        cartproduct.quantity += 1
                        cartproduct.subtotal += product_obj.selling_price
                        cartproduct.save()
                        cart_obj.total += product_obj.selling_price
                        cart_obj.save()
                    else:
                        cartproduct = CartProduct.objects.create(cart=cart_obj,product=product_obj,rate=product_obj.selling_price,quantity=1,subtotal=product_obj.selling_price)
                        cart_obj.total += product_obj.selling_price
                        cart_obj.save()
                else:
                    cart_obj = Cart.objects.create(total=0)
                    cartproduct = CartProduct.objects.create(cart=cart_obj,product=product_obj,rate=product_obj.selling_price,quantity=1,subtotal=product_obj.selling_price)
                    cart_obj.total += product_obj.selling_price
                    cart_obj.save()
                return JsonResponse({'success':True,'msg':'Product Added Successfuly .'})
            
        return JsonResponse({'success':False,'render':True})


def AjaxUrls(request):
    cp_id  = request.POST.get("cp_id",None)
    cp_obj = CartProduct.objects.get(id=cp_id)
    cart_obj = cp_obj.cart
    if request.POST.get('incr'):
        action = request.POST.get('incr')
        if action == "1":
            cp_obj.quantity += 1
            cp_obj.subtotal += cp_obj.rate
            cp_obj.save()
            
            cart_obj.total += cp_obj.rate
            cart_obj.save()
            
            return JsonResponse({'qty':cp_obj.quantity,'subtotal':cp_obj.subtotal,'total':cart_obj.total})
        elif action == "0":
            cp_obj.quantity -= 1
            cp_obj.subtotal -= cp_obj.rate
            cp_obj.save()
            cart_obj.total -= cp_obj.rate
            cart_obj.save()
            
            if cp_obj.quantity == 0:
                cp_obj.delete()
                return JsonResponse({'delete':True,'total':cart_obj.total})
            else:
                return JsonResponse({'qty':cp_obj.quantity,'subtotal':cp_obj.subtotal,'total':cart_obj.total})
        else:
            return JsonResponse({'error':True})
    elif request.POST.get('deleteitem'):
        cart_obj.total -= cp_obj.subtotal
        cart_obj.save()
        cp_obj.delete()
        return JsonResponse({'delete':True,'total':cart_obj.total})
    return JsonResponse({'error':True})


@require_POST
def EmptyCart(request):
    if not (request.user.is_authenticated and not request.user.is_staff):
        return JsonResponse({'error': True}, status=403)
    customer = get_object_or_404(Customer, user_id=request.user)
    cart, _ = Cart.objects.get_or_create(customer=customer, defaults={'total': 0})
    cart.cartproduct.all().delete()
    cart.total = 0
    cart.save()
    return JsonResponse({'error': False})