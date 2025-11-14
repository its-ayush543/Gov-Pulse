import { Link, useLocation } from "react-router-dom";
import { Menu } from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Button } from "@/components/ui/button";
import { Department, departmentNames } from "@/data/newsData";

const Navigation = () => {
  const location = useLocation();
  const departments = Object.keys(departmentNames) as Department[];

  return (
    <nav className="sticky top-0 z-50 bg-card/80 backdrop-blur-lg border-b border-border shadow-sm">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2 group">
            <div className="h-8 w-8 bg-gradient-primary rounded-lg flex items-center justify-center shadow-glow transition-transform group-hover:scale-110">
              <span className="text-primary-foreground font-bold text-sm">GP</span>
            </div>
            <span className="text-xl font-bold bg-gradient-primary bg-clip-text text-transparent">
              GovPulse AI
            </span>
          </Link>

          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" size="sm" className="gap-2">
                <Menu className="h-4 w-4" />
                Departments
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-56 bg-popover">
              {departments.map((dept) => (
                <DropdownMenuItem key={dept} asChild>
                  <Link
                    to={`/department/${dept}`}
                    className={`cursor-pointer ${
                      location.pathname === `/department/${dept}`
                        ? "bg-accent text-accent-foreground"
                        : ""
                    }`}
                  >
                    {departmentNames[dept]}
                  </Link>
                </DropdownMenuItem>
              ))}
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </nav>
  );
};

export default Navigation;
