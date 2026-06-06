import { create } from "zustand";
import { persist } from "zustand/middleware";

interface User {
  id: string;
  email: string;
  full_name: string;
  is_verified: boolean;
}

interface Workspace {
  id: string;
  name: string;
  slug: string;
  role: string;
}

interface AuthState {
  user: User | null;
  workspaces: Workspace[];
  currentWorkspace: Workspace | null;
  setAuth: (user: User, workspaces: Workspace[], tokens: { access_token: string; refresh_token: string }) => void;
  setCurrentWorkspace: (workspace: Workspace) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      workspaces: [],
      currentWorkspace: null,
      setAuth: (user, workspaces, tokens) => {
        localStorage.setItem("access_token", tokens.access_token);
        localStorage.setItem("refresh_token", tokens.refresh_token);
        const ws = workspaces[0] || null;
        if (ws) localStorage.setItem("workspace_id", ws.id);
        set({ user, workspaces, currentWorkspace: ws });
      },
      setCurrentWorkspace: (workspace) => {
        localStorage.setItem("workspace_id", workspace.id);
        set({ currentWorkspace: workspace });
      },
      logout: () => {
        localStorage.clear();
        set({ user: null, workspaces: [], currentWorkspace: null });
      },
    }),
    { name: "auth-storage", partialize: (s) => ({ user: s.user, workspaces: s.workspaces, currentWorkspace: s.currentWorkspace }) }
  )
);
