var _af_handlers = window._af_handlers || null;
var OperatorHandlers = function($) {
	var self = this;
	self.value = null;
	self.val_input = null;
	self.selected_field_elm = null;

	self.add_datepickers = function() {
		var form_id = self.val_input.parents('tr').attr('id');
		var form_num = parseInt(form_id.replace('form-', ''), 10);

		var $from = $('<input type="text" class="form-control">');
		$from.attr("name", "form-" + form_num + "-value_from");
		$from.attr("id", "id_form-" + form_num + "-value_from");
		$from.addClass('query-dt-from');

		self.val_input.parent().prepend($from);
		var val = self.val_input.val();
		if (!val || val == 'null') {
			self.val_input.val("");
		} else {
			from_to = val.split(',');
			if (from_to.length == 2) {
				$from.val(from_to[0])
			}
		}
		self.val_input.css({display: 'none'});

		$(".hasDatepicker").daterangepicker("destroy");
		$from.addClass('vDateField').daterangepicker({locale: {
            format: 'YYYY-MM-DD'
        }});
	};

	self.add_timepickers = function() {
		var form_id = self.val_input.parents('tr').attr('id');
		var form_num = parseInt(form_id.replace('form-', ''), 10);

		var $from = $('<input type="text" class="form-control">');
		$from.attr("name", "form-" + form_num + "-value_from");
		$from.attr("id", "id_form-" + form_num + "-value_from");
		$from.attr("placeholder", 'HH:MM');
		$from.addClass('query-dt-from');

		self.val_input.parent().prepend($from);
		var val = self.val_input.val();
		if (!val || val == 'null') {
			self.val_input.val("");
		} else {
			from_to = val.split(',');
			if (from_to.length == 2) {
				$from.val(from_to[0])
			}
		}
		self.val_input.css({display: 'none'});

		$from.addClass('vTimeField').datetimepicker({
                    format: 'H:m',
                });
	};

	self.remove_datepickers = function() {
		self.val_input.css({display: 'block'});
		if (self.val_input.parent().find('input.vDateField').length > 0) {
			var datefields = self.val_input.parent().find('input.vDateField');
			datefields.each(function() {
				$(this).daterangepicker("destroy");
			});
			datefields.remove();
		}
	};

	self.remove_timepickers = function() {
		self.val_input.css({display: 'block'});
		if (self.val_input.parent().find('input.vTimeField').length > 0) {
			var timefield = self.val_input.parent().find('input.vTimeField');
			timefield.each(function() {
				$(this).datetimepicker("destroy");
			});
			timefield.remove();
		}
	};

	self.remove_boolean = function() {
		self.val_input.attr('type','text')
		
	};

	self.add_boolean = function() {
		self.val_input.attr({'type':'number','min':0,'step':1,'maxlength':1})


	};

	self.modify_widget = function(elm) {
		// pick a widget for the value field according to operator
		self.value = $(elm).val();
		self.val_input = $(elm).parents('tr').find('.query-value');
		console.log("selected operator: " + self.value);
		if (self.value == "daterange") {
			self.remove_timepickers();
			self.remove_boolean()
			self.add_datepickers();

		} 
		else if (self.value == "timerange")
			{
				self.remove_datepickers()
				self.remove_boolean()
				self.add_timepickers();
			}
		else if ((self.value == "istrue") || (self.value == "isfalse"))
			{
				self.remove_datepickers()
				self.remove_timepickers();
				self.add_boolean()

			}
		else {
			self.remove_datepickers();
			self.remove_timepickers();
			self.remove_boolean()
		}
	};

	self.initialize_select2 = function(elm) {
		// initialize select2 widget and populate field choices
		var field = $(elm).val();
		var choices_url = CHOICES_LOOKUP_URL.replace("0",field);
		var input = $(elm).closest('tr').find('input.query-value');
		$.get(choices_url, function(data) {
			console.log(data)
			integer_field = ["iexact","isnull", "lt", "gt", "lte", "gte"]
			string_field = ["iexact","isnull", "icontains", "iregex"]
			date_field = ["daterange"]
			time_field = ["timerange"]
			boolean_field = ["istrue", "isfalse"]
			$(elm).closest('tr').find("select.query-operator > option").each(function() {
			    
			    $(this).addClass('hide')
			    if(data.field_type == "IntegerField" || data.field_type == "FloatField" || data.field_type == "AutoField"){
			    	if(integer_field.indexOf(this.value ) > -1){
			    		$(this).removeClass('hide').removeAttr("selected").attr("selected", "selected");
			    		self.modify_widget(this)
			    	}
			    }
			    else if(data.field_type == "CharField"){
			    	if(string_field.indexOf(this.value ) > -1){
			    		$(this).removeClass('hide').removeAttr("selected").attr("selected", "selected");
			    		self.modify_widget(this)
			    	}
			    }
			    else if (data.field_type == "BooleanField"){
			    	if(boolean_field.indexOf(this.value ) > -1){
			    		$(this).removeClass('hide').removeAttr("selected").attr("selected", "selected");
			    		self.modify_widget(this)
			    	}
			    }
			    else if(data.field_type == "DateField" || data.field_type == "DateTimeField"){
			    	if(date_field.indexOf(this.value ) > -1){
			    		$(this).removeClass('hide').removeAttr("selected").attr("selected", "selected");
			    		self.modify_widget(this)
			    	}
			    }
			    else if(data.field_type == "TimeField"){
			    	if(time_field.indexOf(this.value ) > -1){
			    		$(this).removeClass('hide').removeAttr("selected").attr("selected", "selected");
			    		self.modify_widget(this)
			    	}
			    }
			    else{
			    	$(this).removeClass('hide')
			    	self.modify_widget(this)
			    }

			});

			data.data.forEach(function(value){
				input.append('<option value="'+value+'">' +value+'</option>')
			})
		});
	};

	self.field_selected = function(elm) {
		self.selected_field_elm = elm;
		var row = $(elm).parents('tr');
		var op = row.find('.query-operator');
		var value = row.find('.query-value');
		if ($(elm).val() == "_OR") {
			// op.val("iexact").prop("disabled", true);
			// value.val("null").prop("disabled", true);
			op.after('<input type="hidden" value="' + op.val() +
				'" name="' + op.attr("name") + '">');
			value.after('<input type="hidden" value="' + value.val() +
				'" name="' + value.attr("name") + '">');
		} else {
			// op.prop("disabled", false);
			op.siblings('input[type="hidden"]').remove();
			// value.prop("disabled", false);
			value.siblings('input[type="hidden"]').remove();
			if (!value.val() == "null") {
				value.val("");
			}
			op.val("iexact").change();
			self.initialize_select2(elm);
		}
	};

	self.init = function() {
		var rows = $('[data-rules-formset] tr.form-row');
		if (rows.length == 1 && rows.eq(0).hasClass('empty-form')) {
			// if only 1 form and it's empty, add first extra formset
			$('[data-rules-formset] .add-row a').click();
		}
		$('.form-row select.query-operator').each(function() {
			$(this).off("change");
			$(this).data('pre_change', $(this).val());
			$(this).on("change", function() {
				var before_change = $(this).data('pre_change');
				if ($(this).val() != before_change) self.modify_widget(this);
				$(this).data('pre_change', $(this).val());
			}).change();
		});
		$('.form-row select.query-field').each(function() {
			$(this).off("change");
			$(this).data('pre_change', $(this).val());
			$(this).on("change", function() {
				var before_change = $(this).data('pre_change');
				if ($(this).val() != before_change) self.field_selected(this);
				$(this).data('pre_change', $(this).val());
			}).change();
		});
		// self.field_selected($('.form-row select.query-field').first());

	};

	self.destroy = function() {
		$('.form-row select.query-operator').each(function() {
			$(this).off("change");
		});
		$('.form-row select.query-field').each(function() {
			$(this).off("change");
		});
		
	};
};

// using Grappelli's jquery if available
(function($) {
	$(document).ready(function() {
		if (!_af_handlers) {
			_af_handlers = new OperatorHandlers($);
			_af_handlers.destroy()
			_af_handlers.init();
		}
	});
})(window._jq || jQuery);
