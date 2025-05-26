from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Item, Stock, SoldService, SoldItem, Item
from django.db.models import Prefetch,Sum
from django.db.models.functions import TruncMonth
from .forms import ItemForm, StockForm,InvoiceForm
from django.contrib import messages
from django.shortcuts import get_object_or_404
import random
from django.utils import timezone
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'login.html', {'error': 'Credenciales inválidas'})
    return render(request, 'login.html')

@login_required
def dashboard(request):
    return render(request, 'dashboard.html')

def logout_view(request):
    logout(request)
    return redirect('login')
@login_required
def inventario_view(request):
    items = Item.objects.prefetch_related(
        Prefetch('stock_set', queryset=Stock.objects.all())
    )
    return render(request, 'inventario.html', {'items': items})
@login_required
def manejar_inventario_view(request):
    items = Item.objects.prefetch_related('stock_set')
    item_form = ItemForm()
    stock_form = StockForm()

    # Handle new item
    if 'add_item' in request.POST:
        item_form = ItemForm(request.POST)
        if item_form.is_valid():
            item_form.save()
            return redirect('manejar_inventario')

    # Handle new stock
    if 'add_stock' in request.POST:
        stock_form = StockForm(request.POST)
        if stock_form.is_valid():
            stock_form.save()
            return redirect('manejar_inventario')

    return render(request, 'manejar_inventario.html', {
        'items': items,
        'item_form': item_form,
        'stock_form': stock_form
    })

@login_required
def delete_item(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    item.delete()
    return redirect('manejar_inventario')

@login_required
def delete_stock(request, stock_id):
    stock = get_object_or_404(Stock, id=stock_id)
    stock.delete()
    return redirect('manejar_inventario')

@login_required
def warranty_view(request):
    query = request.GET.get("q", "")
    services = SoldService.objects.filter(warranty__icontains=query) if query else SoldService.objects.all()
    return render(request, "warranty.html", {"services": services, "query": query})

@login_required
def earnings_and_reports_view(request):
    total_earnings = SoldService.objects.aggregate(total=Sum('total_sold'))['total'] or 0

    # Earnings by service type
    service_data = (
        SoldService.objects
        .values('service_type__name')
        .annotate(total=Sum('total_sold'))
        .order_by('-total')
    )
    service_labels = [entry['service_type__name'] for entry in service_data]
    service_totals = [float(entry['total']) for entry in service_data]

    # Items sold count
    item_data = (
        SoldItem.objects
        .values('item__name')
        .annotate(count=Sum('amount'))
        .order_by('-count')
    )
    item_labels = [entry['item__name'] for entry in item_data]
    item_counts = [entry['count'] for entry in item_data]

    # Earnings per month
    monthly_data = (
        SoldService.objects
        .annotate(month=TruncMonth('date'))
        .values('month')
        .annotate(total=Sum('total_sold'))
        .order_by('month')
    )
    month_labels = [entry['month'].strftime('%b %Y') for entry in monthly_data]
    month_totals = [float(entry['total']) for entry in monthly_data]

    context = {
        'total_earnings': total_earnings,
        'service_labels': service_labels,
        'service_totals': service_totals,
        'item_labels': item_labels,
        'item_counts': item_counts,
        'month_labels': month_labels,
        'month_totals': month_totals,
    }
    return render(request, 'earnings_and_reports.html', context)

@login_required
def generar_factura_view(request):
    items = Item.objects.all()
    form = InvoiceForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            service_type = form.cleaned_data['service_type']
            license_plate = form.cleaned_data['license_plate']
            selected_items = request.POST.getlist('item')

            if not selected_items:
                messages.error(request, "Debes seleccionar al menos un ítem.")
                return redirect("generar_factura")

            total = 0
            sold_items_data = []

            for item_id in selected_items:
                try:
                    item = Item.objects.get(id=item_id)
                    quantity_str = request.POST.get(f'quantity_{item_id}', '0')
                    quantity = int(quantity_str)

                    if quantity <= 0:
                        raise ValueError()

                    total += item.price * quantity
                    sold_items_data.append((item, quantity))
                except (Item.DoesNotExist, ValueError):
                    messages.error(request, f"Error con el ítem o cantidad para ID {item_id}.")
                    return redirect("generar_factura")

            # Generate unique warranty number
            warranty = random.randint(100000000, 999999999)
            while SoldService.objects.filter(warranty=warranty).exists():
                warranty = random.randint(100000000, 999999999)

            # Create sold service
            sold_service = SoldService.objects.create(
                service_type=service_type,
                total_sold=total,
                license_plate=license_plate,
                warranty=warranty,
                date=timezone.now()
            )

            # Create sold items and update stock
            for item, quantity in sold_items_data:
                SoldItem.objects.create(sold_service=sold_service, item=item, amount=quantity)

                stock = Stock.objects.filter(item=item).first()
                if stock and stock.amount >= quantity:
                    stock.amount -= quantity
                    stock.save()
                else:
                    messages.warning(request, f"No hay suficiente inventario para {item.name}.")

            messages.success(request, f"Factura generada con éxito. Garantía: {sold_service.warranty}")
            return redirect("generar_factura")

    return render(request, "factura.html", {"items": items, "form": form})
@login_required
def ventas_view(request):
    sold_items_qs = SoldItem.objects.select_related('item')
    sold_services = SoldService.objects.select_related('service_type').prefetch_related(
        Prefetch('solditem_set', queryset=sold_items_qs)
    ).order_by('-date')
    return render(request, "ventas.html", {"sold_services": sold_services})