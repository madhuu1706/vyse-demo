"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { Button, Card, CardBody, Input } from "@/components/ui/primitives";

const STATUSES = ["idea", "script", "shoot", "edit", "review", "posted"];

export default function Flow() {
  const [board, setBoard] = useState<Record<string, any[]>>({});
  const [title, setTitle] = useState("");

  const load = () => api.flow().then(setBoard).catch(() => setBoard({}));
  useEffect(() => { load(); }, []);

  async function add() {
    if (!title.trim()) return;
    await api.createTask({ title, status: "idea" });
    setTitle(""); load();
  }
  async function move(id: string, status: string) {
    await api.moveTask(id, { status }); load();
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Flow</h1>
      <div className="flex gap-2">
        <Input className="max-w-sm" placeholder="New content task…" value={title}
          onChange={(e) => setTitle(e.target.value)} onKeyDown={(e) => e.key === "Enter" && add()} />
        <Button variant="accent" onClick={add}>Add</Button>
      </div>
      <div className="grid grid-cols-2 gap-3 md:grid-cols-3 xl:grid-cols-6">
        {STATUSES.map((s) => (
          <div key={s} className="rounded-xl border border-border bg-panel/40 p-2">
            <div className="mb-2 px-1 text-xs font-medium uppercase text-muted">{s} · {(board[s] || []).length}</div>
            <div className="space-y-2">
              {(board[s] || []).map((t) => (
                <Card key={t.id}><CardBody className="p-3">
                  <div className="text-sm">{t.title}</div>
                  <select value={t.status} onChange={(e) => move(t.id, e.target.value)}
                    className="mt-2 w-full rounded border border-border bg-bg px-1 py-1 text-xs text-muted">
                    {STATUSES.map((x) => <option key={x} value={x}>{x}</option>)}
                  </select>
                </CardBody></Card>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
