// Liveness probe for Docker Compose and CI. A token, never prose (NN-6).
export const dynamic = "force-dynamic";

export function GET() {
  return Response.json({ status: "ok" });
}
