"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { ChevronRight, Home } from "lucide-react";

export function Breadcrumb() {
  const pathname = usePathname();
  
  const segments = pathname.split('/').filter(Boolean);
  
  if (segments.length === 0) {
    return null;
  }

  const breadcrumbs = [
    { label: "Dashboard", href: "/" }
  ];

  let currentPath = "";
  segments.forEach((segment, index) => {
    currentPath += `/${segment}`;
    
    let label = segment;
    if (segment === "users") {
      label = "Users";
    } else if (segment === "conversations") {
      label = "Conversations";
    } else if (segment === "memory") {
      label = "Memory";
    } else if (segment === "expenses") {
      label = "Expenses";
    } else if (segment === "facts") {
      label = "Facts";
    } else if (!isNaN(Number(segment))) {
      const prevSegment = segments[index - 1];
      if (prevSegment === "users") {
        label = `User ${segment}`;
      } else if (prevSegment === "conversations") {
        label = `Conversation ${segment}`;
      } else {
        label = `#${segment}`;
      }
    } else {
      label = segment.charAt(0).toUpperCase() + segment.slice(1);
    }
    
    breadcrumbs.push({
      label,
      href: currentPath
    });
  });

  return (
    <nav className="flex items-center space-x-1 text-sm text-muted-foreground">
      <Home className="w-4 h-4 mr-1" />
      {breadcrumbs.map((item, index) => (
        <div key={item.href} className="flex items-center">
          {index === breadcrumbs.length - 1 ? (
            <span className="font-medium text-foreground">
              {item.label}
            </span>
          ) : (
            <Link 
              href={item.href}
              className="hover:text-foreground transition-colors"
            >
              {item.label}
            </Link>
          )}
          
          {index < breadcrumbs.length - 1 && (
            <ChevronRight className="w-4 h-4 mx-1" />
          )}
        </div>
      ))}
    </nav>
  );
}