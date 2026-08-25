from typing import Any, Dict


def normalize_flow_stress(fstres_data: Dict[str, Any]) -> Dict[str, Any]:
    return {
        'strain': fstres_data.get('strain_data') or [],
        'strain_rate': fstres_data.get('strain_rate_data') or [],
        'temperature': fstres_data.get('temperature_data') or [],
        'stress': fstres_data.get('stress_data') or [],
        'shape': {
            'num_strain': fstres_data.get('num_strain', 0),
            'num_rate': fstres_data.get('num_rate', 0),
            'num_temp': fstres_data.get('num_temp', 0),
        }
    }


def completeness_score(material_data: Dict[str, Any]) -> Dict[str, Any]:
    fields = ['MTNAME', 'UNIT', 'YOUNG', 'POISON', 'THRCND', 'HEATCP', 'MASDEN', 'EMSVTY', 'EXPAND', 'FRAE2H', 'FPERV', 'FSTRES', 'FRCMOD']
    present = [field for field in fields if field in material_data]
    return {
        'score': round(len(present) / len(fields) * 100, 2),
        'present': present,
        'missing': [field for field in fields if field not in material_data],
    }
