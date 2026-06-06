import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function NotFound() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-background p-4 text-center">
      <h1 className="text-6xl font-bold text-gradient">404</h1>
      <p className="mt-4 text-xl font-semibold">Page not found</p>
      <p className="mt-2 text-muted-foreground">The page you&apos;re looking for doesn&apos;t exist.</p>
      <Link href="/" className="mt-8">
        <Button variant="gradient">Go Home</Button>
      </Link>
    </div>
  );
}
