import { http } from './http'

export function convertMaterial(id, targetFormat) {
  return http.post(`/materials/${id}/convert/`, { target_format: targetFormat })
}
