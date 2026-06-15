import Link from "next/link";
import { api } from "@/lib/api";
import { Card, CardBody, EmptyState } from "@/components/ui/primitives";
import { PasteUrlBar } from "@/components/paste-url-bar";

export const dynamic = "force-dynamic";

export default async function Posts() {
  const posts = await api.posts().catch(() => []);
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Posts</h1>
      <PasteUrlBar />
      {posts.length === 0 ? <EmptyState title="No posts yet" hint="Paste a link to ingest." /> : (
        <div className="grid grid-cols-1 gap-3 md:grid-cols-2 lg:grid-cols-3">
          {posts.map((p: any) => (
            <Link key={p.id} href={`/posts/${p.id}`}>
              <Card className="overflow-hidden transition hover:border-accent">
                {p.thumbnail_url && <img src={p.thumbnail_url} alt="" className="aspect-video w-full object-cover" />}
                <CardBody>
                  <div className="text-xs text-muted">{p.platform} · {p.ingest_status}</div>
                  <div className="mt-1 line-clamp-2 text-sm">{p.caption || p.url}</div>
                </CardBody>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
