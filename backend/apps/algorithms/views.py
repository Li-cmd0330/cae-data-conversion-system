from rest_framework.decorators import api_view
from rest_framework.response import Response

from core.algorithms.flow_stress import completeness_score, normalize_flow_stress
from core.algorithms.interpolation import FlowStressInterpolator, linear_interpolate, nearest_interpolate
from core.algorithms.johnson_cook import fit_johnson_cook_placeholder, johnson_cook
from core.algorithms.unit_conversion import convert_unit


@api_view(['POST'])
def interpolate(request):
    method = request.data.get('method', 'linear')
    x = request.data.get('x') or []
    y = request.data.get('y') or []
    target_x = float(request.data.get('target_x'))
    value = nearest_interpolate(x, y, target_x) if method == 'nearest' else linear_interpolate(x, y, target_x)
    return Response({'value': value, 'method': method})


@api_view(['POST'])
def flow_stress_predict(request):
    interpolator = FlowStressInterpolator(request.data.get('fstres_data') or {})
    value = interpolator.predict(
        strain=float(request.data.get('strain')),
        strain_rate=request.data.get('strain_rate'),
        temperature=request.data.get('temperature'),
        method=request.data.get('method', 'linear'),
    )
    return Response({'stress': value})


@api_view(['POST'])
def unit_convert(request):
    value = convert_unit(
        float(request.data.get('value')),
        request.data.get('from_unit'),
        request.data.get('to_unit'),
        request.data.get('quantity'),
    )
    return Response({'value': value})


@api_view(['POST'])
def normalize_fstres(request):
    return Response(normalize_flow_stress(request.data.get('fstres_data') or {}))


@api_view(['POST'])
def material_completeness(request):
    return Response(completeness_score(request.data.get('material_data') or {}))


@api_view(['POST'])
def johnson_cook_value(request):
    params = request.data.get('params') or {}
    value = johnson_cook(
        float(request.data.get('strain')),
        float(request.data.get('strain_rate', 1.0)),
        float(request.data.get('temperature', 20.0)),
        **params,
    )
    return Response({'stress': value})


@api_view(['POST'])
def johnson_cook_fit(request):
    return Response(fit_johnson_cook_placeholder(request.data.get('strain') or [], request.data.get('stress') or []))
