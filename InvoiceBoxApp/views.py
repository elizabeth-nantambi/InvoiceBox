from django.shortcuts import render
from django.views import *
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import *
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.views.generic import DetailView
from django.views.generic.edit import CreateView
from .models import Payment
from django.urls import reverse
from .forms import CustomUserCreationForm
from django.contrib import messages
from django.shortcuts import redirect
from datetime import timedelta, date
from django.db.models import Sum, Count
from django.utils.timezone import now, timedelta
from django.contrib.auth.views import LoginView, LogoutView

class CustomLoginView(LoginView):
    template_name = 'login.html'
    def get_success_url(self):
        user = self.request.user
        if user.role == 'provider':
            return reverse_lazy('provider_dashboard')
        elif user.role == 'purchaser':
            return reverse_lazy('purchaser_dashboard')
        return reverse_lazy('profile_view') 

class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('login')

@login_required
def profile_view(request):
    return render(request, 'profile.html')

def home_view(request):
    return render(request, 'home.html')


@login_required
def provider_dashboard(request):
    if request.user.role != 'provider':
        return render(request, 'unauthorized.html')
    
    invoices = Invoice.objects.filter(provider=request.user)
    paid_count = invoices.filter(status='paid').count()
    pending_count = invoices.filter(status='pending').count()
    return render(request, 'provider_dashboard.html', {
        'invoices': invoices,
        'paid_count': paid_count,
        'pending_count': pending_count
    })

@login_required
def purchaser_dashboard(request):
    if request.user.role != 'purchaser':
        return render(request, 'unauthorized.html')
    
    invoices = Invoice.objects.filter(purchaser=request.user)
    pending_count = invoices.filter(status='pending').count
    paid_count = invoices.filter(status='paid').count()
    return render(request, 'purchaser_dashboard.html', {
        'invoices': invoices,
        'pending_count': pending_count,
        'paid_count': paid_count
    })

class CreateInvoiceView(CreateView):
    model = Invoice
    fields = ['purchaser', 'description', 'amount', 'currency']
    template_name = 'create_invoice.html'
    success_url = reverse_lazy('provider_dashboard')

    def form_valid(self, form):
        form.instance.provider = self.request.user
        form.instance.date_due = date.today() + timedelta(days=7)
        return super().form_valid(form)


class CreateUserView(CreateView):
    model = CustomUser
    form_class = CustomUserCreationForm
    template_name = 'register.html'
    success_url = reverse_lazy('home') 

    def form_valid(self, form):
        user = form.save(commit=False)
        user.save()
        login(self.request, user)
        messages.success(self.request, f'User {user.username} registered successfully.')

        if user.role == 'provider':
            return redirect('provider_dashboard')
        elif user.role == 'purchaser':
            return redirect('purchaser_dashboard')
        return redirect('home')  
        
    
class InvoiceDetailView(DetailView):
    model = Invoice
    template_name = 'invoice_detail.html'

class MakePaymentView(CreateView):
    model = Payment
    fields = ['amount_paid']
    template_name = 'make_payment.html'

    def form_valid(self, form):
        invoice = Invoice.objects.get(id=self.kwargs['pk'])
        form.instance.invoice = invoice
        invoice.status = 'paid' 
        invoice.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('purchaser_dashboard')

@login_required
def provider_analytics(request):
    invoices = Invoice.objects.filter(provider=request.user)
    paid_count = invoices.filter(status='paid').count()
    pending_count = invoices.filter(status='pending').count()
    total_amount_paid = invoices.filter(status='paid').aggregate(total=Sum('amount'))['total'] or 0
    total_amount_pending = invoices.filter(status='pending').aggregate(total=Sum('amount'))['total'] or 0

    
    date_data = []
    for i in range(6, -1, -1):  
        day = now().date() - timedelta(days=i)
        count = invoices.filter(date_created__date=day).count()
        date_data.append({'date': day.strftime('%b %d'), 'count': count})

    context = {
        'paid_count': paid_count,
        'pending_count': pending_count,
        'total_amount_paid': total_amount_paid,
        'total_amount_pending': total_amount_pending,
        'date_data': date_data,
    }
    return render(request, 'analytics.html', context)

@login_required
def purchaser_analytics(request):
    user = request.user

    invoices = Invoice.objects.filter(purchaser=user)
    paid_count = invoices.filter(status='PAID').count()
    pending_count = invoices.filter(status='PENDING').count()
    total_amount_paid = invoices.filter(status='PAID').aggregate(total=Sum('amount'))['total'] or 0
    total_amount_due = invoices.filter(status='PENDING').aggregate(total=Sum('amount'))['total'] or 0

    date_data = (
        invoices
        .extra({'date': "DATE(date_created)"})
        .values('date')
        .annotate(count=Count('id'))
        .order_by('date')
    )

    context = {
        'paid_count': paid_count,
        'pending_count': pending_count,
        'total_amount_paid': total_amount_paid,
        'total_amount_due': total_amount_due,
        'date_data': date_data,
    }

    return render(request, 'purchaser_analytics.html', context)