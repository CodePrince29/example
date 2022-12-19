class WarehouseLocationPrams(object):
	def get_location_params(self,location):
		w_stored_weight=0
		w_excluded_weight = 0
		w_stored_volume = 0
		w_excluded_volume = 0
		entrance_pallets =  location.warehouseentrancepallet_set.filter(werehouse_entrance_confirmation__werehouse_entrance__status = 'finish')
		exit_pallets = location.warehouseexitpallet_set.filter(werehouse_exit_confirmation__werehouse_exit__status= 'finish')  

		for entrance_pallet in entrance_pallets:
			if entrance_pallet.warehouseinventory_set.first().available_total_boxes!=0:
				w_stored_weight += entrance_pallet.boxes * entrance_pallet.werehouse_entrance_confirmation.product.get_available_weight
				w_stored_volume += entrance_pallet.boxes * entrance_pallet.werehouse_entrance_confirmation.product.get_available_volume

		for exit_pallet in exit_pallets:
			if exit_pallet.inventory.available_total_boxes!=0:
				w_excluded_weight += exit_pallet.boxes * exit_pallet.werehouse_exit_confirmation.product.get_available_weight
				w_excluded_volume += exit_pallet.boxes * exit_pallet.werehouse_exit_confirmation.product.get_available_volume
		
		
		final_weight = w_stored_weight-w_excluded_weight
		final_volume = w_stored_volume-w_excluded_volume
		return final_weight,final_volume