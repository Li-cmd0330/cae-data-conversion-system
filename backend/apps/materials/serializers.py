from rest_framework import serializers
from .models import ExportRecord, Material, MaterialFile, ValidationReport


class MaterialFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaterialFile
        fields = ['id', 'filename', 'original_file', 'uploaded_at', 'file_size', 'parse_status']


class ValidationReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = ValidationReport
        fields = ['id', 'material', 'is_valid', 'errors', 'warnings', 'info', 'created_at']


class ExportRecordSerializer(serializers.ModelSerializer):
    download_url = serializers.SerializerMethodField()
    filename = serializers.SerializerMethodField()

    class Meta:
        model = ExportRecord
        fields = ['id', 'material', 'target_format', 'file', 'filename', 'download_url', 'status', 'created_at']

    def get_download_url(self, obj):
        request = self.context.get('request')
        if not obj.file:
            return None
        url = obj.file.url
        return request.build_absolute_uri(url) if request else url

    def get_filename(self, obj):
        return obj.file.name.split('/')[-1] if obj.file else ''


class MaterialSerializer(serializers.ModelSerializer):
    file = MaterialFileSerializer(read_only=True)
    latest_validation = serializers.SerializerMethodField()

    class Meta:
        model = Material
        fields = ['id', 'file', 'name', 'unit_system', 'raw_data', 'normalized_data', 'tags', 'notes', 'is_favorite', 'created_at', 'updated_at', 'latest_validation']

    def get_latest_validation(self, obj):
        report = obj.validation_reports.order_by('-created_at').first()
        if not report:
            return None
        return ValidationReportSerializer(report).data


class MaterialUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = ['name', 'tags', 'notes', 'is_favorite']


class MaterialUploadSerializer(serializers.Serializer):
    file = serializers.FileField()


class MaterialBatchUploadSerializer(serializers.Serializer):
    files = serializers.ListField(child=serializers.FileField(), allow_empty=False)


class MaterialBatchExportSerializer(serializers.Serializer):
    material_ids = serializers.ListField(child=serializers.IntegerField(), allow_empty=False)
    target_format = serializers.ChoiceField(choices=['json', 'csv', 'txt', 'excel', 'abaqus_inp'])
