import { defineStore } from 'pinia'

export const useMaterialStore = defineStore('material', {
  state: () => ({
    currentMaterialId: Number(localStorage.getItem('currentMaterialId')) || null,
    lastUploadResult: null
  }),
  actions: {
    setCurrentMaterial(id) {
      this.currentMaterialId = id
      localStorage.setItem('currentMaterialId', id)
    },
    setUploadResult(result) {
      this.lastUploadResult = result
      if (result?.material_id) this.setCurrentMaterial(result.material_id)
    }
  }
})
