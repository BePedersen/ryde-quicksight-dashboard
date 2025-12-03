import axios from 'axios'

const API = axios.create({
  baseURL: '/api',
  timeout: 10000,
})

export const getPis = () => API.get('/pis')
export const getPi = (id) => API.get(`/pis/${id}`)
export const getPiStatus = (id) => API.get(`/pis/${id}/status`)
export const getPiConfig = (id) => API.get(`/pis/${id}/config`)
export const updatePiConfig = (id, data) => API.post(`/pis/${id}/config`, data)
export const restartPiService = (id) => API.post(`/pis/${id}/restart`)
export const getPiLogs = (id, lines = 20) => API.get(`/pis/${id}/logs?lines=${lines}`)
export const getCities = () => API.get('/cities')

export default API
