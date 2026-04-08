"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { 
  LayoutDashboard, 
  Radar, 
  ChevronRight,
  ChevronLeft,
  Zap,
  Activity
} from "lucide-react";
import { useState } from "react";
import { clsx } from "clsx";

export default function Sidebar() {
  const pathname = usePathname();
  const [isExpanded, setIsExpanded] = useState(false);

  const navItems = [
    { name: "Dashboard", href: "/", icon: LayoutDashboard },
    { name: "Strategy Radar", href: "/watchlist", icon: Radar },
  ];

  return (
    <aside className={clsx(
      "bg-zinc-950 border-r border-zinc-900 transition-all duration-300 flex flex-col relative",
      isExpanded ? "w-64" : "w-20"
    )}>
      {/* Toggle Button */}
      <button 
        onClick={() => setIsExpanded(!isExpanded)}
        className="absolute -right-3 top-10 z-50 bg-zinc-900 border border-zinc-800 rounded-full p-1 text-zinc-400 hover:text-white transition-colors"
      >
        {isExpanded ? <ChevronLeft className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
      </button>

      {/* Logo Area */}
      <div className={clsx("p-6 flex items-center gap-3", !isExpanded && "justify-center")}>
        <div className="bg-zinc-100 p-1.5 rounded-lg shrink-0">
          <Zap className="w-5 h-5 text-black" />
        </div>
        {isExpanded && <span className="font-bold text-xl tracking-tighter truncate">AGN_OS</span>}
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 space-y-2 mt-4">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.name}
              href={item.href}
              title={!isExpanded ? item.name : ""}
              className={clsx(
                "flex items-center gap-3 px-3 py-3 rounded-xl text-sm font-medium transition-all group",
                isActive 
                  ? "bg-zinc-900 text-zinc-100" 
                  : "text-zinc-500 hover:text-zinc-300 hover:bg-zinc-900/50",
                !isExpanded && "justify-center"
              )}
            >
              <Icon className={clsx("w-5 h-5 shrink-0", isActive ? "text-zinc-100" : "text-zinc-500 group-hover:text-zinc-300")} />
              {isExpanded && <span className="truncate">{item.name}</span>}
            </Link>
          );
        })}
      </nav>

      {/* Status indicator */}
      <div className="p-4 mt-auto border-t border-zinc-900/50">
        <div className={clsx(
          "flex items-center gap-2",
          !isExpanded && "justify-center"
        )}>
          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse shrink-0" />
          {isExpanded && <span className="text-[10px] font-mono text-zinc-600 uppercase tracking-widest">Live_System</span>}
        </div>
      </div>
    </aside>
  );
}
