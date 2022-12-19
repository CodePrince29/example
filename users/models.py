# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import Group
from django.shortcuts import reverse



class UserProfile(AbstractUser):
    role = models.ForeignKey(Group, null=True, blank=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    def __str__(self):
        return self.username

    def __unicode__(self):
        return unicode(self.username)

    def get_absolute_url(self):
        return reverse('user-list')

    @property
    def get_client_product_access(self):
    	if (self.role and self.role.name in ["Direccion","Sistemas"]):
    		return True
    	else:
    		return False

    @property        
    def get_direccion_access(self):
        if (self.role and self.role.name in ["Direccion"]):
            return True
        else:
            return False

    def get_catalog_access(self):
        if (self.role and self.role.name in ["Sistemas","Jefe Almacen","Jefe Administracion"]):
            return True
        else:
            return False

    @property
    def get_jafe_administracion_access(self):
        if (self.role and self.role.name in ["Sistemas","Jefe Almacen","Jefe Administracion"]):
            return True
        else:
            return False

    @property
    def get_control_access(self):
        if (self.role and self.role.name in ["Control","Sistemas","Jefe Almacen","Jefe Administracion"]):
            return True
        else:
            return False

    @property
    def get_control_menu_access(self):
        if (self.role and self.role.name in ["Control"]):
            return True
        else:
            return False

    @property
    def get_entrance_exit_access(self):
        if (self.role and self.role.name in ["Sistemas","Control","Jefe Administracion","Direccion"]):
            return True
        else:
            return False

    @property
    def get_catalog_warehouse_access(self):       
        if (self.role and self.role.name in ["Jefe Almacen","Jefe Administracion"]):
            return True
        else:
            return False

    @property
    def get_syatema_access(self):       
	if (self.role and self.role.name in ["Sistemas"]):
            return True
        else:
            return False
    @property
    def responsable_de_turno_almacen(self):       
        if (self.role and self.role.name in ["Responsable de Turno Almacen"]):
            return True
        else:
            return False
            
    @property
    def get_jefeadministration_access(self):
        if (self.role and self.role.name in ["Jefe Administracion"]):
            return True
        else:
            return False

    @property
    def get_inventory_access(self):
        if (self.role and self.role.name in ["Inventarios"]):

            return True
        else:
            return False

    @property
    def get_warehouseshiftsupervisor_access(self):
        if (self.role and self.role.name in ["Responsable de Turno Almacen"]):
            return True
        else:
            return False

    @property
    def get_jefealmacen_access(self):
        if (self.role and self.role.name in ["Jefe Almacen"]):
            print("Jefe")
            return True
        else:
            return False

    @property
    def jefedeadministracion(self):
        if (self.role and self.role.name in ["Jefe de Administracion"]):
            return True
        else:
            return False
    @property
    def almacen_maniobras(self):
        if (self.role and self.role.name in ["Almacen Maniobras"]):
            return True
        else:
            return False

    @property
    def get_client(self):
        if (self.role_id==None):
            return True
        else:
            return False

    @property
    def not_hide_boxes_values(self):
        """
        SGA-FEAT#Mar26_3 Do not show summary information for some warehouse user roles: We need to do a feature to allow a “Blind Entrance” and “Blind Exit” for the following roles: 

        Jefe Almacen
        Almacen Maniobras
        Responsable Turno Almacen

        For those roles the information about the summary of the product entered must not be visible so they are forced to count and weight the boxes.
        """
        if (self.role and self.role.name in ["Almacen Maniobras", "Jefe Almacen", "Responsable de Turno Almacen"]):
            return False
        else:
            return True
    
