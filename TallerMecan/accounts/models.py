import random
from django.db import models
from django.utils import timezone
class Item(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2) 

    def __str__(self):
        return self.name

class Stock(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField()
    location = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.item.name} - {self.location} ({self.amount})"
    
class ServiceType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class SoldService(models.Model):
    service_type = models.ForeignKey(ServiceType, on_delete=models.CASCADE)
    total_sold = models.DecimalField(max_digits=10, decimal_places=2)
    warranty = models.CharField(max_length=9, unique=True, editable=False)
    license_plate = models.CharField(max_length=20)
    date = models.DateField(default=timezone.now)  # <-- NEW

    def save(self, *args, **kwargs):
        if not self.warranty:
            self.warranty = self.generate_unique_warranty()
        super().save(*args, **kwargs)

    def generate_unique_warranty(self):
        import random
        while True:
            number = str(random.randint(100000000, 999999999))
            if not SoldService.objects.filter(warranty=number).exists():
                return number

    def __str__(self):
        return f"{self.service_type.name} - {self.license_plate}"
    
class SoldItem(models.Model):
    sold_service = models.ForeignKey(SoldService, on_delete=models.CASCADE, related_name='sold_items')
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.item.name} x{self.amount} for {self.sold_service.license_plate}"