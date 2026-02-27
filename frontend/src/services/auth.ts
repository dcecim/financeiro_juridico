import api from '../lib/api';
import { LoginResponse, User } from './types';

export const authService = {
  async login(username: string, password: string, otpCode?: string): Promise<LoginResponse> {
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);

    let url = '/auth/token';
    if (otpCode) {
      url += `?otp_code=${otpCode}`;
    }

    const response = await api.post<LoginResponse>(url, formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    return response.data;
  },

  async getProfile(): Promise<User> {
    const response = await api.get<User>('/auth/me');
    return response.data;
  },

  async setup2FA(): Promise<{ secret: string; otpauth_url: string }> {
    const response = await api.post('/auth/2fa/setup');
    return response.data;
  },

  async activate2FA(code: string): Promise<void> {
    await api.post(`/auth/2fa/activate?code=${code}`);
  },

  async disable2FA(): Promise<void> {
    await api.post('/auth/2fa/disable');
  }
};
