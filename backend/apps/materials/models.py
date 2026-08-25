from django.db import models


class MaterialFile(models.Model):
    filename = models.CharField(max_length=255)
    original_file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file_size = models.PositiveIntegerField(default=0)
    parse_status = models.CharField(max_length=32, default='pending')

    def __str__(self):
        return self.filename


class Material(models.Model):
    file = models.ForeignKey(MaterialFile, on_delete=models.CASCADE, related_name='materials')
    name = models.CharField(max_length=255, blank=True)
    unit_system = models.IntegerField(null=True, blank=True)
    raw_data = models.JSONField(default=dict)
    normalized_data = models.JSONField(default=dict)
    tags = models.CharField(max_length=500, blank=True, default='')
    notes = models.TextField(blank=True, default='')
    is_favorite = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name or f'Material {self.pk}'


class ValidationReport(models.Model):
    material = models.ForeignKey(Material, on_delete=models.CASCADE, related_name='validation_reports')
    is_valid = models.BooleanField(default=False)
    errors = models.JSONField(default=list)
    warnings = models.JSONField(default=list)
    info = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)


class ExportRecord(models.Model):
    material = models.ForeignKey(Material, on_delete=models.CASCADE, related_name='exports')
    target_format = models.CharField(max_length=32)
    file = models.FileField(upload_to='exports/', null=True, blank=True)
    status = models.CharField(max_length=32, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
