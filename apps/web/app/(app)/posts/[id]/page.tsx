import { api } from "@/lib/api";
import { Card, CardBody, Badge } from "@/components/ui/primitives";

export const dynamic = "force-dynamic";

function Row({ k, v }: { k: string; v: any }) {
  return <div className="flex justify-between border-b border-border py-1.5 text-sm">
    <span className="text-muted">{k}</span><span className="text-right">{Array.isArray(v) ? v.join(", ") : (v ?? "—")}</span>
  </div>;
}

export default async function PostDetail({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const p = await api.post(id).catch(() => null);
  if (!p) return <p className="text-muted">Post not found.</p>;
  const a = p.analysis, o = p.outlier, w = p.reasoning;
  return (
    <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
      <div className="space-y-4">
        <h1 className="text-xl font-semibold">{p.platform} post</h1>
        {p.embed_html ? (
          <div className="overflow-hidden rounded-xl border border-border [&_iframe]:w-full"
            dangerouslySetInnerHTML={{ __html: p.embed_html }} />
        ) : p.thumbnail_url ? (
          <img src={p.thumbnail_url} alt="" className="w-full rounded-xl border border-border" />
        ) : (
          <Card><CardBody className="text-sm text-muted">No embed preview available for this platform.</CardBody></Card>
        )}
        <p className="text-sm text-muted">{p.caption}</p>
        <a href={p.url} target="_blank" className="text-sm text-accent">Open original ↗</a>
      </div>

      <div className="space-y-4">
        <Card><CardBody>
          <div className="mb-2 flex items-center justify-between">
            <h2 className="text-sm font-medium">SPIKE · outlier</h2>
            {o && <Badge kind={o.outlier_type}>{o.outlier_type} · {Number(o.score).toFixed(2)}</Badge>}
          </div>
          {o ? <>
            <Row k="eng ratio" v={o.components?.eng_ratio} />
            <Row k="velocity" v={o.components?.velocity} />
            <Row k="retention" v={o.components?.retention} />
          </> : <p className="text-sm text-muted">Not scored yet.</p>}
        </CardBody></Card>

        <Card><CardBody>
          <h2 className="mb-2 text-sm font-medium">PULSE · analysis</h2>
          {a ? <>
            <Row k="hook" v={a.hook_type} /><Row k="cta" v={a.cta_type} />
            <Row k="emotion" v={a.emotion} /><Row k="story" v={a.story_pattern} />
            <Row k="pillar" v={a.content_pillar} />
          </> : <p className="text-sm text-muted">Pending analysis.</p>}
        </CardBody></Card>

        <Card><CardBody>
          <h2 className="mb-2 text-sm font-medium">WHY · reasoning</h2>
          {w ? <>
            <p className="text-sm">{w.why_it_worked}</p>
            <div className="mt-2 flex flex-wrap gap-1">{(w.trigger_type || []).map((t: string) => <Badge key={t}>{t}</Badge>)}</div>
            <p className="mt-2 text-sm text-muted">{w.replication_insights}</p>
          </> : <p className="text-sm text-muted">Reasoning runs only for detected outliers.</p>}
        </CardBody></Card>
      </div>
    </div>
  );
}
