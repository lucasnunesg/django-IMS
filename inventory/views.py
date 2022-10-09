from django.shortcuts import render, get_object_or_404, redirect
from .models import Inventory
from django.contrib.auth.decorators import login_required
from .forms import AddInventoryForm, UpdateInventoryForm
from django.contrib import messages
from django_pandas.io import read_frame
from django.db import models
import plotly
import plotly.express as px
import json
import datetime


@login_required
def inventory_list(request):
    inventories = Inventory.objects.all()
    context = {
        "title": "Inventory List",
        "inventories": inventories
    }
    return render(request, "inventory/inventory_list.html", context=context)


@login_required
def per_product_view(request, pk):
    inventory = get_object_or_404(Inventory, pk=pk)
    context = {
        "inventory": inventory,
        "title": "Product View"
    }

    return render(request, "inventory/per_product.html", context=context)


@login_required
def add_product(request):
    if request.method == "POST":
        add_form = AddInventoryForm(data=request.POST)
        if add_form.is_valid():
            new_inventory = add_form.save(commit=False)
            new_inventory.sales = float(add_form.data['cost_per_item']) * float(add_form.data['quantity_sold'])
            new_inventory.save()
            messages.success(request, "Successfully added product!")
            return redirect("/inventory/")
    else:
        add_form = AddInventoryForm()
    return render(request, "inventory/inventory_add.html", {"form": add_form, "title": "Manage Inventory"})


@login_required
def delete_inventory(request, pk):
    inventory = get_object_or_404(Inventory, pk=pk)
    inventory.delete()
    messages.warning(request, "Successfully deleted product!")
    return redirect("/inventory/")


@login_required
def update_inventory(request, pk):
    inventory = get_object_or_404(Inventory, pk=pk)
    if request.method == "POST":
        updateForm = UpdateInventoryForm(data=request.POST)
        if updateForm.is_valid():
            inventory.quantity_in_stock = updateForm.data['quantity_in_stock']
            inventory.quantity_sold = updateForm.data['quantity_sold']
            inventory.cost_per_item = updateForm.data['cost_per_item']
            inventory.sales = float(inventory.cost_per_item) * float(inventory.quantity_sold)
            inventory.last_sales_date = models.DateField(default=datetime.date.today)
            inventory.save()
            messages.success(request, "Inventory updated!")
            return redirect(f"/inventory/per_product/{pk}")
    else:
        updateForm = UpdateInventoryForm(instance=inventory)

    context = {"form": updateForm, "product_name": inventory.name}
    return render(request, "inventory/inventory_update.html", context=context)


@login_required
def dashboard(request):
    inventories = Inventory.objects.all()

    df = read_frame(inventories)

    sales_graph = df.groupby(by="last_sales_date", as_index=False, sort=True)['sales'].sum()
    sales_graph = px.line(sales_graph, x=sales_graph.last_sales_date,
                          y=sales_graph.sales,
                          title="Sales Trend").update_layout(xaxis_title="Sales",
                                                             yaxis_title="Quantity Sold",
                                                             title_x=0.5,
                                                             xaxis=dict(tickformat="%d/%m/%y", tickmode='linear'))
    sales_graph = json.dumps(sales_graph, cls=plotly.utils.PlotlyJSONEncoder)

    best_performing_product_df = df.groupby(by="name").sum().sort_values(by="quantity_sold")
    best_performing_product = px.bar(best_performing_product_df,
                                     x=best_performing_product_df.index,
                                     y=best_performing_product_df.quantity_sold,
                                     title="Best Performing Product").update_layout(xaxis_title="Product name",
                                                                                    yaxis_title="Quantity Sold",
                                                                                    title_x=0.5)
    best_performing_product = json.dumps(best_performing_product, cls=plotly.utils.PlotlyJSONEncoder)

    most_product_in_stock_df = df.groupby(by="name").sum().sort_values(by="quantity_in_stock")
    most_product_in_stock = px.pie(most_product_in_stock_df,
                                   names=most_product_in_stock_df.index,
                                   values=most_product_in_stock_df.quantity_in_stock,
                                   title="Product Stock overview").update_layout(xaxis_title="Product name",
                                                                                 yaxis_title="Quantity In Stock",
                                                                                 title_x=0.5)
    most_product_in_stock = json.dumps(most_product_in_stock, cls=plotly.utils.PlotlyJSONEncoder)

    context = {
        "sales_graph": sales_graph,
        "best_performing_product": best_performing_product,
        "most_product_in_stock": most_product_in_stock,
        "title": "Product Dashboard"
    }
    return render(request, "inventory/dashboard.html", context=context)
