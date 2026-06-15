import { api } from "@/lib/api";
import { Card, CardBody, Badge, EmptyState } from "@/components/ui/primitives";

export const dynamic = "force-dynamic";

export default async function Vault() {
  const items = await api.vault().catch(() => []);
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Vault</h1>
      <p className="text-sm text-muted">Saved posts, notes, and inspiration boards. Semantic search via embeddings.</p>
      {items.length === 0 ? <EmptyState title="Vault is empty" hint="Save analyzed posts to build inspiration boards." /> : (
        <div className="grid grid-cols-1 gap-3 md:grid-cols-2 lg:grid-cols-3">
          {items.map((v: any) => (
            <Card key={v.id}><CardBody>
              <div className="text-xs text-muted">{v.board || "Unsorted"}</div>
              <p className="mt-1 text-sm">{v.notes || "—"}</p>
              <div className="mt-2 flex flex-wrap gap-1">{(v.tags || []).map((t: string) => <Badge key={t}>{t}</Badge>)}</div>
            </CardBody></Card>
          ))}
        </div>
      )}
    </div>
  );
}
