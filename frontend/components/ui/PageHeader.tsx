import { cn } from "@/lib/utils";

interface PageHeaderProps {
  title: string;
  subtitle?: string;
  icon?: React.ReactNode;
  action?: React.ReactNode;
  className?: string;
}

export function PageHeader({ title, subtitle, icon, action, className }: PageHeaderProps) {
  return (
    <div className={cn(
      "sticky top-0 z-20 border-b border-white/5 bg-[#04070f]/92 backdrop-blur-xl",
      className
    )}>
      <div className="max-w-350 mx-auto px-8 h-16.25 flex items-center justify-between">
        <div className="flex items-center gap-3.5">
          {icon && (
            <div className="w-9 h-9 rounded-xl bg-sky-500/10 border border-sky-500/15 flex items-center justify-center text-sky-400 shrink-0">
              {icon}
            </div>
          )}
          <div>
            <h1
              className="text-[17px] font-bold text-white tracking-tight leading-tight"
              style={{ fontFamily: "var(--font-heading, 'Plus Jakarta Sans', sans-serif)" }}
            >
              {title}
            </h1>
            {subtitle && (
              <p className="text-[11.5px] text-slate-500 mt-0.5 leading-tight">{subtitle}</p>
            )}
          </div>
        </div>
        {action && <div className="shrink-0">{action}</div>}
      </div>
    </div>
  );
}
