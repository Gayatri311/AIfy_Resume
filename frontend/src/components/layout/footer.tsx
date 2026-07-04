import Link from "next/link";

export function Footer() {
  return (
    <footer className="border-t border-border bg-background py-8">
      <div className="mx-auto flex max-w-7xl flex-col items-center justify-between gap-4 px-4 sm:flex-row sm:px-6 lg:px-8">
        <p className="text-sm text-muted-foreground">
          © {new Date().getFullYear()} Alfy Resume. All rights reserved.
        </p>
        <div className="flex gap-6 text-sm text-muted-foreground">
          <Link href="#" className="hover:text-primary">Privacy Policy</Link>
          <Link href="#" className="hover:text-primary">Terms of Service</Link>
          <Link href="#" className="hover:text-primary">Contact Us</Link>
        </div>
      </div>
    </footer>
  );
}
