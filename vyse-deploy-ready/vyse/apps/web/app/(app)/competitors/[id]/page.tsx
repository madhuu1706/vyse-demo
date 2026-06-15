import { api } from "@/lib/api";
import { Card, CardBody } from "@/components/ui/primitives";
import { fmt } from "@/lib/utils";

export const dynamic = "force-dynamic";

export default async function CompetitorDetail({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const all = await api.competitors().catch(() => []);
  const c = all.find((x: any) => x.id === id);
  if (!c) return <p className="text-muted">Competitor not found.</p>;
  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-2xl font-semibold">@{c.handle}</h1>
        <p className="text-sm text-muted">{c.platform} · {c.niche || "uncategorised"}</p>
      </header>
      <div className="grid grid-cols-3 gap-4">
        <Card><CardBody><div className="text-xs text-muted">Followers</div><div className="font-mono text-xl">{fmt(c.followers)}</div></CardBody></Card>
        <Card><CardBody><div className="text-xs text-muted">Engagement</div><div className="font-mono text-xl">{c.engagement_rate ?? "—"}</div></CardBody></Card>
        <Card><CardBody><div className="text-xs text-muted">Avg eng.</div><div className="font-mono text-xl">{fmt(c.account_avg_eng)}</div></CardBody></Card>
      </div>
      <p className="text-sm text-muted">Profile metrics populate once the fetch_profile job runs (wire YouTube Data API key).</p>
    </div>
  );
}
