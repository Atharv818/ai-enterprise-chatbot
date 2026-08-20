import client from './client'

export interface AuthResponse {
  access_token: string
  token_type: string
}

export async function register(email: string, password: string, tenantName: string) {
  const response = await client.post<AuthResponse>('/auth/register', {
    email,
    password,
    tenant_name: tenantName,
  })
  return response.data
}

export async function login(email: string, password: string) {
  const response = await client.post<AuthResponse>('/auth/login', {
    email,
    password,
  })
  return response.data
}
