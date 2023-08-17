from django.shortcuts import render,get_object_or_404,reverse,redirect
from .models import Product,OrderDetail
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse,HttpResponseNotFound
import stripe,json
from .forms import ProductForm,UserRegistrationForm
from django.db.models import Sum
import datetime
from django.views import View
from rest_framework import viewsets
from .serializers import ProductSerializer
from django.views.generic.edit import FormView, DeleteView, CreateView, UpdateView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib.auth.models import User


# Create your views here.

# def index(request):
#     products = Product.objects.all()
#     return render(request,'myapp/index.html',{'products':products})

class IndexView(ListView):
    model = Product
    template_name = 'myapp/index.html'
    context_object_name = 'products'
    
    def get_queryset(self):
        return Product.objects.all()

class ProductViewSet(viewsets.ModelViewSet):
    # querset = Product.objects.all()
    serializer_class = ProductSerializer
    queryset = Product.objects.all()

# def detail(request,id):
    
#     product = Product.objects.get(id=id)
#     stripe_publishable_key = settings.STRIPE_PUBLISHABLE_KEY
#     return render(request,'myapp/detail.html',{'product':product,'stripe_publishable_key':stripe_publishable_key})

class ProductDetailView(DetailView):
    model = Product
    template_name = 'myapp/detail.html'
    context_object_name = 'product'
    pk_url_kwarg = 'id'  

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['stripe_publishable_key'] = settings.STRIPE_PUBLISHABLE_KEY
        return context

# url_local = settings.BASE_URL
# @csrf_exempt
# def create_checkout_session(request,id):
#     request_data = json.loads(request.body)
#     product = Product.objects.get(id=id)
#     stripe.api_key = settings.STRIPE_SECRET_KEY
#     checkout_session = stripe.checkout.Session.create(
#         customer_email = request_data['email'],
#         payment_method_types = ['card'],
#         line_items = [
#             {
#                 'price_data':{
#                     'currency':'usd',
#                     'product_data':{
#                         'name':product.name,
#                     },
#                     'unit_amount':int(product.price * 100)
#                 },
#                 'quantity':1,
#             }
#         ],
#         mode='payment',
#         metadata = {
#             "product_id": product.id,
#             "amount": product.price,
#             "customer_email": request_data['email'],
#         },
#         success_url = url_local +"/success/?session_id={CHECKOUT_SESSION_ID}",
#         cancel_url = request.build_absolute_uri(reverse('failed')),
#     )
#     return JsonResponse({'sessionId':checkout_session.id})


class CheckoutSessionView(View):
    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        request_data = json.loads(request.body)
        product = Product.objects.get(id=kwargs['id'])
        stripe.api_key = settings.STRIPE_SECRET_KEY
        checkout_session = stripe.checkout.Session.create(
            customer_email=request_data['email'],
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data':{
                        'currency':'usd',
                        'product_data':{
                            'name':product.name,
                        },
                        'unit_amount':int(product.price * 100)
                    },
                    'quantity':1,
                }
            ],
            mode='payment',
            metadata={
                "product_id": product.id,
                "amount": product.price,
                "customer_email": request_data['email'],
            },
            success_url=settings.BASE_URL + "/success/?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=request.build_absolute_uri(reverse('failed')),
        )
        return JsonResponse({'sessionId': checkout_session.id})

# def payment_success_view(request):
    
#     session_id = request.GET.get('session_id')
#     if session_id is None:
#         return HttpResponseNotFound()
#     stripe.api_key = settings.STRIPE_SECRET_KEY
#     session = stripe.checkout.Session.retrieve(session_id)
#     payment_intent = stripe.PaymentIntent.retrieve(session.payment_intent)
#     customer_email = session.metadata.get('customer_email', '')
#     product_id = session.metadata.get('product_id', '')
#     amount = session.metadata.get('amount', '')
#     get_product = Product.objects.get(id=product_id)
#     create_order = OrderDetail.objects.create(stripe_payment_intent = payment_intent.id,
#      customer_email=customer_email, product=get_product, amount= int(float(amount)), has_paid=True)

#     product = Product.objects.get(id=create_order.product.id)
#     product.total_sales_amount = product.total_sales_amount + int(product.price)
#     product.total_sales = product.total_sales + 1
#     product.save()
#     return render(request,'myapp/payment_success.html',{'order':create_order})

class PaymentSuccessView(TemplateView):
    template_name = 'myapp/payment_success.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        session_id = self.request.GET.get('session_id')
        if session_id is None:
            raise HttpResponseNotFound()

        stripe.api_key = settings.STRIPE_SECRET_KEY
        session = stripe.checkout.Session.retrieve(session_id)
        payment_intent = stripe.PaymentIntent.retrieve(session.payment_intent)
        customer_email = session.metadata.get('customer_email', '')
        product_id = session.metadata.get('product_id', '')
        amount = session.metadata.get('amount', '')

        get_product = Product.objects.get(id=product_id)
        create_order = OrderDetail.objects.create(
            stripe_payment_intent=payment_intent.id,
            customer_email=customer_email,
            product=get_product,
            amount=int(float(amount)),
            has_paid=True
        )

        product = Product.objects.get(id=create_order.product.id)
        product.total_sales_amount = product.total_sales_amount + int(product.price)
        product.total_sales = product.total_sales + 1
        product.save()

        context['order'] = create_order
        return context

# def payment_failed_view(request):
#     return render(request,'myapp/failed.html')


class PaymentFailedView(TemplateView):
    template_name = 'myapp/failed.html'

# def create_product(request):
#     if request.method == "POST":
#         product_form = ProductForm(request.POST,request.FILES)
#         if product_form.is_valid():
#             new_product = product_form.save(commit=False)
#             new_product.seller = request.user 
#             new_product.save()
#             return redirect('index')


#     product_form = ProductForm()
#     return render(request,'myapp/create_product.html',{'product_form':product_form})

class CreateProductView(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'myapp/create_product.html'
    success_url = reverse_lazy('index')
    login_url = reverse_lazy('login')

    def form_valid(self, form):
        form.instance.seller = self.request.user
        return super().form_valid(form)



# def product_edit(request,id):
#     product = Product.objects.get(id=id)
#     if product.seller != request.user:
#         return redirect('invalid')
#     product_form = ProductForm(request.POST or None,request.FILES or None,instance=product)
#     if request.method == "POST":
#         if product_form.is_valid():
#             product_form.save()
#             return redirect('index')
#     return render(request,'myapp/product_edit.html',{'product_form':product_form,'product':product})


class ProductEditView(UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'myapp/product_edit.html'
    context_object_name = 'product'
    pk_url_kwarg = 'id'

    def dispatch(self, request, *args, **kwargs):
        product = self.get_object()
        if product.seller != request.user:
            return redirect('invalid')
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('index')


# def product_delete(request,id):
#     product = Product.objects.get(id=id)
#     if product.seller != request.user:
#         return redirect('invalid')
#     if request.method == "POST":
#         product.delete()
#         return redirect('index')

#     return render(request,'myapp/delete.html',{'product':product})

class ProductDeleteView(DeleteView):
    model = Product
    template_name = 'myapp/delete.html'
    context_object_name = 'product'
    pk_url_kwarg = 'id'
    success_url = reverse_lazy('index')

    def dispatch(self, request, *args, **kwargs):
        product = self.get_object()
        if product.seller != request.user:
            return redirect('invalid')
        return super().dispatch(request, *args, **kwargs)

# def dashboard(request):
#     products = Product.objects.filter(seller=request.user)
#     return render(request,'myapp/dashboard.html',{'products':products})

class DashboardView(LoginRequiredMixin,ListView):
    model = Product
    template_name = 'myapp/dashboard.html'
    context_object_name = 'products'
    login_url = reverse_lazy('login') 

    def get_queryset(self):
        return Product.objects.filter(seller=self.request.user)

# def register(request):
#     if request.method == 'POST':
#         user_form = UserRegistrationForm(request.POST)
#         new_user = user_form.save(commit=False) 
#         new_user.set_password(user_form.cleaned_data['password'])
#         new_user.save()
#         return redirect('index')
#     user_form = UserRegistrationForm()
#     return render(request,'myapp/register.html',{'user_form':user_form})

class RegisterView(FormView):
    template_name = 'myapp/register.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        # Set the password and save the user
        form.instance.set_password(form.cleaned_data['password'])
        form.save()
        return super().form_valid(form)



# def invalid(request):
#     return render(request,'myapp/invalid.html')

class InvalidView(View):
    template_name = 'myapp/invalid.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

# def my_purchases(request):
#     orders = OrderDetail.objects.filter(customer_email=request.user.email)
#     return render(request,'myapp/purchases.html',{'orders':orders})

class MyPurchasesView(LoginRequiredMixin, ListView):
    model = OrderDetail
    template_name = 'myapp/purchases.html'
    context_object_name = 'orders'
    login_url = reverse_lazy('login')

    def get_queryset(self):
        return OrderDetail.objects.filter(customer_email=self.request.user.email)




class SalesView(LoginRequiredMixin,TemplateView):
    template_name = 'myapp/sales.html'
    login_url = reverse_lazy('login')
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Total sales
        context['total_sales'] = OrderDetail.objects.filter(product__seller=self.request.user).aggregate(Sum('amount'))

        # 365 days sales sum
        last_year = datetime.date.today() - datetime.timedelta(days=365)
        context['yearly_sales'] = OrderDetail.objects.filter(product__seller=self.request.user, created_on__gt=last_year).aggregate(Sum('amount'))

        # 30 days sales sum
        last_month = datetime.date.today() - datetime.timedelta(days=30)
        context['monthly_sales'] = OrderDetail.objects.filter(product__seller=self.request.user, created_on__gt=last_month).aggregate(Sum('amount'))

        # 7 days sales sum
        last_week = datetime.date.today() - datetime.timedelta(days=7)
        context['weekly_sales'] = OrderDetail.objects.filter(product__seller=self.request.user, created_on__gt=last_week).aggregate(Sum('amount'))

        # Everyday sum for the past 30 days
        daily_sales_sums = OrderDetail.objects.filter(product__seller=self.request.user).values('created_on__date').order_by('created_on__date').annotate(sum=Sum('amount'))
        context['daily_sales_sums'] = daily_sales_sums

        # Product sales sums
        product_sales_sums = OrderDetail.objects.filter(product__seller=self.request.user).values('product__name').order_by('product__name').annotate(sum=Sum('amount'))
        context['product_sales_sums'] = product_sales_sums

        return context