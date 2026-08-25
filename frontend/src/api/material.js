import { http } from './http'

export function uploadMaterial(file) {
  const form = new FormData()
  form.append('file', file)
  return http.post('/materials/upload/', form)
}

export function uploadMaterials(files) {
  const form = new FormData()
  files.forEach(file => form.append('files', file))
  return http.post('/materials/batch-upload/', form)
}

export function batchConvertMaterials(materialIds, targetFormat) {
  return http.post('/materials/batch-convert/', {
    material_ids: materialIds,
    target_format: targetFormat
  })
}

export function clearMaterialHistory() {
  return http.delete('/materials/clear-history/')
}

export function compareMaterials(materialIds) {
  return http.post('/materials/compare/', { material_ids: materialIds })
}

export function getStatistics() {
  return http.get('/materials/statistics/')
}

export function listMaterials() {
  return http.get('/materials/')
}

export function getMaterial(id) {
  return http.get(`/materials/${id}/`)
}

export function validateMaterial(id) {
  return http.post(`/materials/${id}/validate/`)
}

export function getFlowStressChart(id) {
  return http.get(`/materials/${id}/charts/flow-stress/`)
}

export function getCompletenessChart(id) {
  return http.get(`/materials/${id}/charts/completeness/`)
}
