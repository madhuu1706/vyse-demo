"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import { fmt } from "@/lib/utils";
import { Button, Card, CardBody, Input, EmptyState } from "@/components/ui/primitives";

export default function Competitors() {
  const [items, setItems] = useState<any[]>([]);
  const [platform, setPlatform] = useState("youtube");
  const [handle, setHandle] = useState("");

  const load = () => api.competitors().then(setItems).catch(() => setItems([]));
  useEffect(() => { load(); }, []);

  async function add() {
    if (!handle.trim()) return;
    await api.addCompetitor({ platform, handle });
    setHandle(""); load();
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Competitors</h1>
      <Card><CardBody className="flex flex-wrap items-center gap-2">
        <select value={platform} onChange={(e) => setPlatform(e.target.value)}
          className="rounded-lg border border-border bg-bg px-3 py-2 text-sm">
          {["youtube", "tiktok", "instagram", "linkedin"].map((p) => <option key={p}>{p}</option>)}
        </select>
        <Input className="max-w-xs" placeholder="@handle" value={handle}
          onChange={(e) => setHandle(e.target.value)} onKeyDown={(e) => e.key === "Enter" && add()} />
        <Button variant="accent" onClick={add}>Add competitor</Button>
      </CardBody></Card>
      {items.length === 0 ? <EmptyState title="No competitors yet" hint="Add a handle to start tracking." /> : (
        <div className="grid grid-cols-1 gap-3 md:grid-cols-2 lg:grid-cols-3">
          {items.map((c) => (
            <Link key={c.id} href={`/competitors/${c.id}`}>
              <Card className="transition hover:border-accent"><CardBody>
                <div className="flex items-center justify-between">
                  <span className="font-medium">@{c.handle}</span>
                  <span className="text-xs text-muted">{c.platform}</span>
                </div>
                <div className="mt-3 flex gap-4 text-sm text-muted">
                  <span>{fmt(c.followers)} followers</span>
                  <span>{c.niche || "uncategorised"}</span>
                </div>
              </CardBody></Card>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
