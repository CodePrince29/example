# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
import datetime, pdb
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import View
from django.views.generic.list import ListView
from .models import ReserveInventory,ReserveInventoryLog
from django.http import JsonResponse
from catalogs.warehouse.models import WarehouseInventory
from .forms import (ReserveInventoryForm)
from django.views.decorators.csrf import csrf_exempt
from .serializers import InventorySerializer
from django.contrib import messages

class InventoryReservedList(LoginRequiredMixin, ListView):
  template_name = 'warehouse/reserve_inventory/list.html'
  model = ReserveInventory

  def get_queryset(self):
    queryset = ReserveInventory.objects.filter(released_store_box__gt= 0).order_by('-created_at')
    return queryset


class InventoryReservedCreate(LoginRequiredMixin, CreateView):
    template_name = 'warehouse/reserve_inventory/create.html'
    model = ReserveInventory
    form_class = ReserveInventoryForm
    def form_valid(self, form):
      instance = form.save()
      instance.created_by = self.request.user
      instance.save()
      inventory = instance.inventory  
      retained_boxes = inventory.retained_boxes+instance.reserve_boxes
      inventory.retained_boxes = retained_boxes
      inventory.available_total_boxes = inventory.total_boxes-retained_boxes
      inventory.save()
      from warehouses.warehouse_entrance.models import WarehouseEntrancePallet
      entrance_pallet = inventory.warehouse_entrance_pallet
      WarehouseEntrancePallet.objects.filter(id=entrance_pallet.id).update(retained_quantity = retained_boxes, retained_reason = instance.motive_to_reserve)
      try:
        warehouse_location = inventory.warehouse_location
        warehouse_location.total_retained_boxes =sum(warehouse_location.warehouseinventory_set.all().values_list('retained_boxes', flat=True))
        warehouse_location.save()
      except:
        pass

      return super(InventoryReservedCreate, self).form_valid(form)


class InventoryReservedUpdate(LoginRequiredMixin, UpdateView):
    template_name = 'warehouse/reserve_inventory/detail.html'
    model = ReserveInventory
    form_class = ReserveInventoryForm
    def form_valid(self, form):
      original_reserve_boxes = self.object.original_reserve_boxes

      if self.object.original_released_store_box == 0:
        messages.error(self.request, 'No puedes cambiar esto')
        return HttpResponseRedirect(reverse_lazy('inventory-reserve-list'))
      else:
        instance = form.save()
        inventory = instance.inventory  
        inventory.retained_boxes = instance.reserve_boxes
        if original_reserve_boxes - instance.reserve_boxes == 0: # full release
          available_total_boxes = original_reserve_boxes
        elif original_reserve_boxes - instance.reserve_boxes < 0: # more boxes retained
          available_total_boxes = inventory.available_total_boxes - (inventory.retained_boxes - original_reserve_boxes)
        else:
          available_total_boxes = inventory.available_total_boxes + (original_reserve_boxes - inventory.retained_boxes)

        inventory.available_total_boxes = available_total_boxes
        inventory.save()

        from warehouses.warehouse_entrance.models import WarehouseEntrancePallet
        entrance_pallet = inventory.warehouse_entrance_pallet
        WarehouseEntrancePallet.objects.filter(id=entrance_pallet.id).update(retained_quantity = instance.reserve_boxes, retained_reason = instance.motive_to_reserve)
        try:
          warehouse_location = inventory.warehouse_location
          warehouse_location.total_retained_boxes =sum(warehouse_location.warehouseinventory_set.all().values_list('retained_boxes', flat=True))
          warehouse_location.save()
        except:
          pass

      return super(InventoryReservedUpdate, self).form_valid(form)


@csrf_exempt
def filter_inventory(request):
  client = request.POST['customer']
  product = request.POST['product']
  lote_tarima = request.POST['lote_tarima']
  lote_cliente = request.POST['lote_cliente']
  expiry_date = request.POST['expiry_date']
  query_list = {}
  if client != "":
    query_list.update({"client": client})
  if product != "":
    query_list.update({"product": product})
  if lote_tarima != "":
    query_list.update({"warehouse_entrance_pallet__palet_lot": lote_tarima})
  if lote_cliente != "":
    query_list.update({"warehouse_entrance_pallet__cost_lot": lote_cliente})
  if expiry_date != "":
    query_list.update({"exp_date": expiry_date})
  inventories = WarehouseInventory.objects.filter(**query_list)
  if len(inventories) > 0:    
    inventory_data = InventorySerializer(inventories,many=True)  
    locations_data = {'filter_inventory': inventory_data.data, 'code': 200}
    return JsonResponse(locations_data, safe=True)
  else:
    locations_data = {'filter_inventory': [], 'code': 500}
    return JsonResponse(locations_data, safe=True)

@csrf_exempt
def release_reserved_inventory(request):  
  try:
    inventory = request.POST['inventory']
    release_box = request.POST['release_box']
    notes = request.POST['notes']
    instance = ReserveInventory.objects.get(id=request.POST.get('reserve_id'))
    instance.notes = notes
    released_store_box = instance.released_store_box - float(release_box)
    if released_store_box == 0:
      release_boxes = instance.released_store_box # Total boxes released
    else:
      release_boxes = released_store_box # Partial released

    instance.released_store_box = released_store_box
    instance.save()

    inventory = instance.inventory
    released_boxes = int(inventory.retained_boxes - float(release_box))
    if released_boxes < 0:
      released_boxes=0
    WarehouseInventory.objects.filter(id=inventory.id).update(retained_boxes=released_boxes, available_total_boxes=inventory.available_total_boxes+int(release_box))
    entrance_pallet = inventory.warehouse_entrance_pallet
    from warehouses.warehouse_entrance.models import WarehouseEntrancePallet
    WarehouseEntrancePallet.objects.filter(id=entrance_pallet.id).update(retained_quantity = released_boxes)

    try:
      warehouse_location = inventory.warehouse_location
      warehouse_location.total_retained_boxes = sum(warehouse_location.warehouseinventory_set.all().values_list('retained_boxes', flat=True))
      warehouse_location.save()
    except:
      pass
    user = request.user
    log_reserve_inv = ReserveInventoryLog.objects.create(release_boxes=float(release_box), notes=notes, inventory=inventory, user=user, reserveinventory=instance)
    response_data = {'reserveinventory_box': instance.released_store_box, 'code': 200}
    return JsonResponse(response_data, safe=True)
  except:
    response_data = {'reserveinventory_box': 0, 'code': 500}
    return JsonResponse(response_data, safe=True)
  
