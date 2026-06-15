"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { Button, Input } from "@/components/ui/primitives";

export function PasteUrlBar() {
  const [url, setUrl] = useState("");
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");
  const router = useRouter();

  async function go() {
    if (!url.trim()) return;
    setBusy(true); setErr("");
    try {
      const r = await api.ingest(url.trim());
      router.push(`/posts/${r.post_id}`);
    } catch (e: any) {
      setErr(String(e.message || e));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="flex flex-col gap-2">
      <div className="flex gap-2">
        <Input
          placeholder="Paste a YouTube / TikTok / Instagram / LinkedIn URL…"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && go()}
        />
        <Button variant="accent" onClick={go} disabled={busy}>
          {busy ? "Ingesting…" : "Analyze"}
        </Button>
      </div>
      {err && <p className="text-xs text-viral">{err}</p>}
    </div>
  );
}
