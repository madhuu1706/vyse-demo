import Link from "next/link";
import { api } from "@/lib/api";
import { Card, CardBody, Badge, EmptyState } from "@/components/ui/primitives";

export const dynamic = "force-dynamic";

export default async function Outliers() {
  const rows = await api.outliers("?limit=50").catch(() => []);
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Outliers</h1>
      <p className="text-sm text-muted">Ranked by SPIKE score. Top performers surface automatically.</p>
      {rows.length === 0 ? <EmptyState title="No outliers yet" hint="Ingest posts; scoring runs in the pipeline." /> : (
        <Card><CardBody className="p-0">
          <table className="w-full text-sm">
            <thead className="text-left text-xs uppercase text-muted">
              <tr className="border-b border-border">
                <th className="p-3">#</th><th className="p-3">Post</th><th className="p-3">Platform</th>
                <th className="p-3">Type</th><th className="p-3 text-right">Score</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r: any, i: number) => (
                <tr key={r.post_id} className="border-b border-border hover:bg-panel">
                  <td className="p-3 font-mono text-muted">{i + 1}</td>
                  <td className="p-3"><Link href={`/posts/${r.post_id}`} className="hover:text-accent">{r.caption || r.url}</Link></td>
                  <td className="p-3 text-muted">{r.platform}</td>
                  <td className="p-3"><Badge kind={r.outlier_type}>{r.outlier_type}</Badge></td>
                  <td className="p-3 text-right font-mono">{Number(r.score).toFixed(2)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </CardBody></Card>
      )}
    </div>
  );
}
