import axios, { AxiosInstance, AxiosResponse } from 'axios'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// Create axios instance
const api: AxiosInstance = axios.create({
    baseURL: API_BASE_URL,
    timeout: 30000,
    headers: {
        'Content-Type': 'application/json',
    },
})

// Request interceptor to add auth token
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('access_token')
        if (token) {
            config.headers.Authorization = `Bearer ${token}`
        }
        return config
    },
    (error) => Promise.reject(error)
)

// Response interceptor for error handling
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            localStorage.removeItem('access_token')
            window.location.href = '/login'
        }
        return Promise.reject(error)
    }
)

// Auth API
export const authAPI = {
    login: (email: string, password: string) =>
        api.post('/api/v1/auth/login', { email, password }),

    register: (userData: {
        email: string
        password: string
        full_name: string
        niche?: string
    }) => api.post('/api/v1/auth/register', userData),

    refreshToken: () => api.post('/api/v1/auth/refresh'),

    logout: () => api.post('/api/v1/auth/logout'),

    getCurrentUser: () => api.get('/api/v1/auth/me'),
}

// Content API
export const contentAPI = {
    generateIdeas: (data: {
        topic: string
        niche?: string
        audience?: string
        count: number
        platform?: string
    }) => api.post('/api/v1/content/generate-ideas', data),

    repurposeVideo: (formData: FormData) =>
        api.post('/api/v1/content/repurpose-video', formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
            timeout: 120000, // 2 minutes for video processing
        }),

    getHistory: (params?: {
        content_type?: string
        limit?: number
        offset?: number
    }) => api.get('/api/v1/content/history', { params }),

    deleteContent: (contentId: string) =>
        api.delete(`/api/v1/content/${contentId}`),
}

// Analytics API
export const analyticsAPI = {
    getDashboard: (timeframe: string = '30d') =>
        api.get('/api/v1/analytics/dashboard', { params: { timeframe } }),

    getPerformanceMetrics: (platform?: string) =>
        api.get('/api/v1/analytics/performance', { params: { platform } }),

    getContentInsights: (contentId: string) =>
        api.get(`/api/v1/analytics/content/${contentId}/insights`),

    getCompetitorAnalysis: (competitor: string) =>
        api.get('/api/v1/analytics/competitors', { params: { competitor } }),
}

// Monetization API
export const monetizationAPI = {
    getBrandDeals: () => api.get('/api/v1/monetization/deals'),

    createBrandOutreach: (data: {
        brand_name: string
        email: string
        proposal_type: string
        custom_message?: string
    }) => api.post('/api/v1/monetization/outreach', data),

    calculateRates: (data: {
        platform: string
        followers: number
        engagement_rate: number
        content_type: string
    }) => api.post('/api/v1/monetization/calculate-rates', data),

    trackDeal: (data: {
        brand_name: string
        deal_value: number
        status: string
        deadline?: string
    }) => api.post('/api/v1/monetization/deals', data),
}

// Copyright API
export const copyrightAPI = {
    getMonitoringStatus: () => api.get('/api/v1/copyright/monitoring'),

    setupContentMonitoring: (data: {
        content_url: string
        content_type: string
        monitoring_frequency: string
    }) => api.post('/api/v1/copyright/monitor', data),

    getViolations: () => api.get('/api/v1/copyright/violations'),

    submitDMCA: (violationId: string) =>
        api.post(`/api/v1/copyright/violations/${violationId}/dmca`),
}

export default api
