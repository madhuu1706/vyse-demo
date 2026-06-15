import { Card, CardBody } from "@/components/ui/primitives";

export default function Settings() {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Settings</h1>
      <Card><CardBody className="space-y-2 text-sm">
        <div className="flex justify-between"><span className="text-muted">Workspace</span><span>Dev Workspace</span></div>
        <div className="flex justify-between"><span className="text-muted">Plan</span><span>agency (dev)</span></div>
        <div className="flex justify-between"><span className="text-muted">Auth mode</span><span>dev — no Clerk required</span></div>
      </CardBody></Card>
      <Card><CardBody className="text-sm text-muted">
        Billing (Stripe), members, and API usage wire in via the <code>/v1/billing</code> and
        Clerk endpoints. See the README for going to production.
      </CardBody></Card>
    </div>
  );
}
