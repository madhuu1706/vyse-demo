import { api } from "@/lib/api";
import { Card, CardBody, Stat } from "@/components/ui/primitives";
import { PasteUrlBar } from "@/components/paste-url-bar";

export const dynamic = "force-dynamic";

export default async function Dashboard() {
  const [posts, comps, outliers] = await Promise.all([
    api.posts().catch(() => []),
    api.competitors().catch(() => []),
    api.outliers().catch(() => []),
  ]);
  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-2xl font-semibold">Dashboard</h1>
        <p className="text-sm text-muted">Discover → analyze → understand → recreate.</p>
      </header>
      <PasteUrlBar />
      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        <Stat label="Competitors" value={comps.length} />
        <Stat label="Posts" value={posts.length} />
        <Stat label="Outliers" value={outliers.length} />
        <Stat label="Top score" value={outliers[0]?.score?.toFixed(1) ?? "—"} />
      </div>
      <Card>
        <CardBody>
          <h2 className="mb-3 text-sm font-medium text-muted">Recent posts</h2>
          {posts.length === 0 ? (
            <p className="text-sm text-muted">Paste a URL above to ingest your first post.</p>
          ) : (
            <ul className="divide-y divide-border">
              {posts.slice(0, 8).map((p: any) => (
                <li key={p.id} className="flex items-center justify-between py-2 text-sm">
                  <span className="truncate">{p.caption || p.url}</span>
                  <span className="text-muted">{p.platform}</span>
                </li>
              ))}
            </ul>
          )}
        </CardBody>
      </Card>
    </div>
  );
}
