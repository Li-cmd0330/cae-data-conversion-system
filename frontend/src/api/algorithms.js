import { http } from './http'

export function interpolate(payload) {
  return http.post('/algorithms/interpolate/', payload)
}

export function flowStressPredict(payload) {
  return http.post('/algorithms/flow-stress/predict/', payload)
}

export function normalizeFlowStress(payload) {
  return http.post('/algorithms/flow-stress/normalize/', payload)
}

export function materialCompleteness(payload) {
  return http.post('/algorithms/completeness/', payload)
}

export function unitConvert(payload) {
  return http.post('/algorithms/unit-convert/', payload)
}

export function fitJohnsonCook(payload) {
  return http.post('/algorithms/johnson-cook/fit/', payload)
}
