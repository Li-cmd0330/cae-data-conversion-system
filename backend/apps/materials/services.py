import re
from pathlib import Path
from typing import Any, Dict, Iterable, List

from django.conf import settings

from core.exporters.abaqus_exporter import AbaqusMaterialExporter
from core.exporters.excel_exporter import ExcelExporter
from core.exporters.multi_format_exporter import MultiFormatExporter
from core.parsers.deform_key_parser import DEFORMKeyParser
from core.validators.material_validator import DataValidator
from core.intelligence.material_classifier import MaterialClassifier
from core.intelligence.data_repair import IntelligentDataRepair
from .models import ExportRecord, Material, MaterialFile, ValidationReport


class MaterialService:
    @staticmethod
    def parse_uploaded_file(uploaded_file) -> Dict[str, Any]:
        material_file = MaterialFile.objects.create(
            filename=uploaded_file.name,
            original_file=uploaded_file,
            file_size=uploaded_file.size,
            parse_status='parsing',
        )
        try:
            parser = DEFORMKeyParser(material_file.original_file.path)
            parsed_data = parser.parse()
            material = Material.objects.create(
                file=material_file,
                name=parsed_data.get('MTNAME', {}).get('name', ''),
                unit_system=parsed_data.get('UNIT'),
                raw_data=parsed_data,
                normalized_data=parsed_data,
            )
            
            # 智能材料识别
            classifier = MaterialClassifier()
            classification = classifier.classify(
                filename=uploaded_file.name,
                properties=parsed_data
            )
            
            # 自动添加标签
            if classification['confidence'] > 0.5:
                existing_tags = [t.strip() for t in material.tags.split(',') if t.strip()] if material.tags else []
                new_tags = classification['tags']
                all_tags = list(set(existing_tags + new_tags))
                material.tags = ', '.join(all_tags)
                material.save(update_fields=['tags'])
            
            # 智能数据修复分析
            repair_engine = IntelligentDataRepair()
            repair_analysis = repair_engine.analyze_and_repair(
                material_data=parsed_data,
                material_type=classification.get('type', 'unknown')
            )
            
            # 查找相似材料
            similar_materials = classifier.find_similar_materials(
                material_type=classification.get('type', 'unknown'),
                limit=5
            )
            
            validation = MaterialService.validate_material(material)
            MaterialService._delete_uploaded_source_file(material_file)
            material_file.parse_status = 'success'
            material_file.save(update_fields=['parse_status', 'original_file'])
            
            return {
                'material': material,
                'validation': validation,
                'classification': classification,
                'repair_analysis': repair_analysis,
                'similar_materials': similar_materials
            }
        except Exception:
            MaterialService._delete_uploaded_source_file(material_file)
            material_file.parse_status = 'failed'
            material_file.save(update_fields=['parse_status', 'original_file'])
            raise

    @staticmethod
    def parse_uploaded_files(uploaded_files: Iterable[Any]) -> List[Dict[str, Any]]:
        results = []
        for uploaded_file in uploaded_files:
            result = MaterialService.parse_uploaded_file(uploaded_file)
            results.append(result)
        return results

    @staticmethod
    def validate_material(material: Material) -> ValidationReport:
        validator = DataValidator()
        is_valid, errors, warnings, info = validator.validate(material.normalized_data or material.raw_data)
        return ValidationReport.objects.create(
            material=material,
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            info=info,
        )

    @staticmethod
    def _delete_uploaded_source_file(material_file: MaterialFile):
        if material_file.original_file:
            storage = material_file.original_file.storage
            name = material_file.original_file.name
            if name and storage.exists(name):
                storage.delete(name)
            material_file.original_file.name = ''


class ExportService:
    EXTENSIONS = {
        'json': 'json',
        'csv': 'csv',
        'txt': 'txt',
        'excel': 'xlsx',
        'abaqus_inp': 'inp',
    }

    @staticmethod
    def export_material(material: Material, target_format: str) -> ExportRecord:
        if target_format not in ExportService.EXTENSIONS:
            raise ValueError(f'不支持的导出格式: {target_format}')

        record = ExportRecord.objects.create(material=material, target_format=target_format, status='running')
        export_dir = Path(settings.MEDIA_ROOT) / 'exports'
        export_dir.mkdir(parents=True, exist_ok=True)
        extension = ExportService.EXTENSIONS[target_format]
        safe_name = ExportService._build_export_filename(material, extension)
        output_path = export_dir / safe_name
        data = material.normalized_data or material.raw_data

        try:
            if target_format == 'abaqus_inp':
                AbaqusMaterialExporter(data).save(str(output_path))
            elif target_format == 'excel':
                ExcelExporter(include_charts=False, include_validation=True).create_material_template(data, str(output_path))
            else:
                exporter = MultiFormatExporter()
                method = getattr(exporter, f'export_to_{target_format}')
                ok = method(data, str(output_path))
                if not ok:
                    raise RuntimeError('导出失败')

            record.file.name = f'exports/{safe_name}'
            record.status = 'success'
            record.save(update_fields=['file', 'status'])
            return record
        except Exception:
            record.status = 'failed'
            record.save(update_fields=['status'])
            raise

    @staticmethod
    def export_materials(material_ids: Iterable[int], target_format: str) -> List[ExportRecord]:
        records = []
        for material in Material.objects.filter(id__in=list(material_ids)).select_related('file'):
            records.append(ExportService.export_material(material, target_format))
        return records

    @staticmethod
    def _build_export_filename(material: Material, extension: str) -> str:
        original_name = material.file.filename if material.file and material.file.filename else material.name or f'material_{material.id}'
        stem = Path(original_name).stem
        safe_stem = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '_', stem).strip().strip('.')
        safe_stem = re.sub(r'_+', '_', safe_stem)
        if not safe_stem:
            safe_stem = f'material_{material.id}'
        return f'{safe_stem}.{extension}'
