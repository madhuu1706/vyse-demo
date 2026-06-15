// Thin API client. In dev, Next rewrites /api/* -> FastAPI. Auth header is added
// here once Clerk is wired; dev mode needs none.
const base = "/api";

async function req<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${base}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...(init?.headers || {}) },
    cache: "no-store",
  });
  if (!res.ok) throw new Error(`${res.status} ${await res.text()}`);
  return res.status === 204 ? (undefined as T) : res.json();
}

export const api = {
  competitors: () => req<any[]>("/v1/competitors"),
  addCompetitor: (b: any) => req("/v1/competitors", { method: "POST", body: JSON.stringify(b) }),
  posts: () => req<any[]>("/v1/posts"),
  post: (id: string) => req<any>(`/v1/posts/${id}`),
  ingest: (url: string) => req<any>("/v1/posts/ingest", { method: "POST", body: JSON.stringify({ url }) }),
  outliers: (q = "") => req<any[]>(`/v1/outliers${q}`),
  forge: (b: any) => req<any>("/v1/forge", { method: "POST", body: JSON.stringify(b) }),
  vault: () => req<any[]>("/v1/vault"),
  saveVault: (b: any) => req("/v1/vault", { method: "POST", body: JSON.stringify(b) }),
  flow: () => req<Record<string, any[]>>("/v1/flow"),
  createTask: (b: any) => req("/v1/flow", { method: "POST", body: JSON.stringify(b) }),
  moveTask: (id: string, b: any) => req(`/v1/flow/${id}`, { method: "PATCH", body: JSON.stringify(b) }),
};
