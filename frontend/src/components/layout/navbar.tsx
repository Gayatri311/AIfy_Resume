"use client";

import Link from "next/link";
import { FileText } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

const navLinks = [
  { href: "#features", label: "Features" },
  { href: "#how-it-works", label: "How it Works" },
  { href: "#faq", label: "FAQ" },
];

interface NavbarProps {
  activeLink?: string;
  showCta?: boolean;
}

export function Navbar({ activeLink = "Features", showCta = true }: NavbarProps) {
  return (
    <header className="sticky top-0 z-50 border-b border-border/50 bg-background/80 backdrop-blur-lg">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        <Link href="/" className="flex items-center gap-2">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary/10">
            <FileText className="h-5 w-5 text-primary" />
          </div>
          <span className="text-lg font-bold text-foreground">Alfy Resume</span>
        </Link>

        <nav className="hidden items-center gap-8 md:flex">
          {navLinks.map((link) => (
            <Link
              key={link.label}
              href={link.href}
              className={cn(
                "text-sm font-medium transition-colors hover:text-primary",
                activeLink === link.label
                  ? "text-primary underline decoration-primary decoration-2 underline-offset-8"
                  : "text-muted-foreground"
              )}
            >
              {link.label}
            </Link>
          ))}
        </nav>

        {showCta && (
          <div className="flex items-center gap-2">
            <Button asChild size="sm">
              <Link href="/upload">Alfy My Resume</Link>
            </Button>
          </div>
        )}
      </div>
    </header>
  );
}
