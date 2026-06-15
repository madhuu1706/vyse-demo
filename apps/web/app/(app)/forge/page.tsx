"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { Button, Card, CardBody, Input } from "@/components/ui/primitives";

export default function Forge() {
  const [posts, setPosts] = useState<any[]>([]);
  const [src, setSrc] = useState("");
  const [brand, setBrand] = useState("");
  const [niche, setNiche] = useState("");
  const [out, setOut] = useState<any>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => { api.posts().then(setPosts).catch(() => {}); }, []);

  async function run() {
    if (!src || !brand) return;
    setBusy(true);
    try {
      const bp = await api.forge({ source_post_id: src, target_brand: brand, target_niche: niche });
      setOut(bp.output);
    } finally { setBusy(false); }
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Forge</h1>
      <p className="text-sm text-muted">Turn a winning post into a production-ready blueprint for your brand.</p>
      <Card><CardBody className="space-y-3">
        <select value={src} onChange={(e) => setSrc(e.target.value)}
          className="w-full rounded-lg border border-border bg-bg px-3 py-2 text-sm">
          <option value="">Select a source post…</option>
          {posts.map((p) => <option key={p.id} value={p.id}>{p.caption || p.url}</option>)}
        </select>
        <Input placeholder="Target brand" value={brand} onChange={(e) => setBrand(e.target.value)} />
        <Input placeholder="Target niche (optional)" value={niche} onChange={(e) => setNiche(e.target.value)} />
        <Button variant="accent" onClick={run} disabled={busy}>{busy ? "Forging…" : "Generate blueprint"}</Button>
      </CardBody></Card>
      {out && (
        <Card><CardBody className="space-y-3 text-sm">
          <div><span className="text-muted">Framework:</span> {out.framework}</div>
          <div><span className="text-muted">Hooks:</span><ul className="ml-4 list-disc">{out.hooks?.map((h: string, i: number) => <li key={i}>{h}</li>)}</ul></div>
          <div><span className="text-muted">Script:</span><p className="whitespace-pre-wrap">{out.script}</p></div>
          <div><span className="text-muted">Shot list:</span><ul className="ml-4 list-disc">{out.shotlist?.map((s: string, i: number) => <li key={i}>{s}</li>)}</ul></div>
          <div><span className="text-muted">CTAs:</span> {out.ctas?.join(" · ")}</div>
        </CardBody></Card>
      )}
    </div>
  );
}
