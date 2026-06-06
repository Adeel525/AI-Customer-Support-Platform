import axios, { AxiosError, InternalAxiosRequestConfig } from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export const api = axios.create({
  baseURL: API_URL,
  headers: { "Content-Type": "application/json" },
});

api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("access_token");
    const workspaceId = localStorage.getItem("workspace_id");
    if (token) config.headers.Authorization = `Bearer ${token}`;
    if (workspaceId) config.headers["X-Workspace-Id"] = workspaceId;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const original = error.config;
    if (error.response?.status === 401 && original && !(original as { _retry?: boolean })._retry) {
      (original as { _retry?: boolean })._retry = true;
      const refreshToken = localStorage.getItem("refresh_token");
      if (refreshToken) {
        try {
          const { data } = await axios.post(`${API_URL}/auth/refresh`, {
            refresh_token: refreshToken,
          });
          localStorage.setItem("access_token", data.access_token);
          localStorage.setItem("refresh_token", data.refresh_token);
          original.headers.Authorization = `Bearer ${data.access_token}`;
          return api(original);
        } catch {
          localStorage.clear();
          window.location.href = "/login";
        }
      }
    }
    return Promise.reject(error);
  }
);

export const authApi = {
  signup: (data: { email: string; password: string; full_name: string; workspace_name: string }) =>
    api.post("/auth/signup", data),
  login: (data: { email: string; password: string }) => api.post("/auth/login", data),
  me: () => api.get("/auth/me"),
  forgotPassword: (email: string) => api.post("/auth/forgot-password", { email }),
  resetPassword: (token: string, new_password: string) =>
    api.post("/auth/reset-password", { token, new_password }),
  verifyEmail: (token: string) => api.post("/auth/verify-email", { token }),
};

export const workspaceApi = {
  getCurrent: () => api.get("/workspaces/current"),
  update: (data: Record<string, unknown>) => api.patch("/workspaces/current", data),
  updateBranding: (data: Record<string, unknown>) => api.patch("/workspaces/current/branding", data),
  listMembers: () => api.get("/workspaces/current/members"),
  inviteMember: (email: string, role: string) =>
    api.post("/workspaces/current/members", { email, role }),
};

export const knowledgeApi = {
  upload: (file: File) => {
    const form = new FormData();
    form.append("file", file);
    return api.post("/knowledge/documents/upload", form, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
  list: (skip = 0, limit = 50) => api.get("/knowledge/documents", { params: { skip, limit } }),
  delete: (id: string) => api.delete(`/knowledge/documents/${id}`),
  stats: () => api.get("/knowledge/stats"),
};

export const chatbotApi = {
  list: () => api.get("/chatbots"),
  get: (id: string) => api.get(`/chatbots/${id}`),
  create: (data: Record<string, unknown>) => api.post("/chatbots", data),
  update: (id: string, data: Record<string, unknown>) => api.patch(`/chatbots/${id}`, data),
  delete: (id: string) => api.delete(`/chatbots/${id}`),
};

export const ticketApi = {
  list: (status?: string) => api.get("/tickets", { params: { status } }),
  get: (id: string) => api.get(`/tickets/${id}`),
  create: (data: Record<string, unknown>) => api.post("/tickets", data),
  update: (id: string, data: Record<string, unknown>) => api.patch(`/tickets/${id}`, data),
  addComment: (id: string, content: string, is_internal = false) =>
    api.post(`/tickets/${id}/comments`, { content, is_internal }),
  listComments: (id: string) => api.get(`/tickets/${id}/comments`),
};

export const analyticsApi = {
  overview: () => api.get("/analytics/overview"),
  historical: (start: string, end: string) =>
    api.get("/analytics/historical", { params: { start_date: start, end_date: end } }),
  csat: () => api.get("/analytics/csat"),
};

export const crawlerApi = {
  list: () => api.get("/crawler/jobs"),
  create: (url: string, schedule = "weekly") =>
    api.post("/crawler/jobs", { url, schedule }),
  sync: (id: string) => api.post(`/crawler/jobs/${id}/sync`),
};

export const chatApi = {
  listConversations: (status?: string) =>
    api.get("/chat/conversations", { params: { status } }),
  getConversation: (id: string) => api.get(`/chat/conversations/${id}`),
};
