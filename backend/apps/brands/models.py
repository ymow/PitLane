"""
Brand and supplier models for PitLane F1 platform.
"""
from django.db import models
from config.utils import generate_id


class Manufacturer(models.Model):
    """
    Car manufacturers and constructors (Ferrari, Mercedes, McLaren, etc.)
    """
    id = models.CharField(max_length=25, primary_key=True, default=generate_id, editable=False)
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True, db_index=True)
    country = models.CharField(max_length=100)
    founded_year = models.IntegerField()
    logo_url = models.URLField(null=True, blank=True)
    website = models.URLField(null=True, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'manufacturers'
        ordering = ['name']

    def __str__(self):
        return self.name


class EngineSupplier(models.Model):
    """
    Engine manufacturers (Mercedes HPP, Ferrari, Honda, Renault, etc.)
    """
    id = models.CharField(max_length=25, primary_key=True, default=generate_id, editable=False)
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True, db_index=True)
    manufacturer = models.ForeignKey(Manufacturer, null=True, blank=True, on_delete=models.SET_NULL)
    country = models.CharField(max_length=100)
    logo_url = models.URLField(null=True, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'engine_suppliers'
        ordering = ['name']

    def __str__(self):
        return self.name


class TireSupplier(models.Model):
    """
    Tire manufacturers (Pirelli, Bridgestone, Michelin - series-wide contracts)
    """
    id = models.CharField(max_length=25, primary_key=True, default=generate_id, editable=False)
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    logo_url = models.URLField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tire_suppliers'
        ordering = ['name']

    def __str__(self):
        return self.name


class ComponentSupplier(models.Model):
    """
    Suppliers for specific component types (brakes, fuel, lubricants, etc.)
    """
    COMPONENT_TYPE_CHOICES = [
        ('BRAKE', 'Brake System'),
        ('FUEL', 'Fuel'),
        ('LUBRICANT', 'Lubricant'),
        ('HYDRAULIC', 'Hydraulic System'),
        ('ELECTRONICS', 'Electronics'),
        ('SUSPENSION', 'Suspension'),
    ]

    id = models.CharField(max_length=25, primary_key=True, default=generate_id, editable=False)
    name = models.CharField(max_length=100)
    component_type = models.CharField(max_length=50, choices=COMPONENT_TYPE_CHOICES, db_index=True)
    country = models.CharField(max_length=100)
    logo_url = models.URLField(null=True, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'component_suppliers'
        ordering = ['component_type', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_component_type_display()})"


class Sponsor(models.Model):
    """
    Commercial sponsors (title, team, and driver sponsors)
    """
    id = models.CharField(max_length=25, primary_key=True, default=generate_id, editable=False)
    name = models.CharField(max_length=100)
    industry = models.CharField(max_length=100, null=True, blank=True)
    logo_url = models.URLField(null=True, blank=True)
    website = models.URLField(null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'sponsors'
        ordering = ['name']

    def __str__(self):
        return self.name
