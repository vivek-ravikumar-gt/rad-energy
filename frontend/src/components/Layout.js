import { Outlet, Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, Building2, Map, Network, Zap, Mail, Menu, Search } from 'lucide-react';
import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Sheet, SheetContent, SheetTrigger } from '@/components/ui/sheet';

const Layout = () => {
  const location = useLocation();
  const [open, setOpen] = useState(false);

  const navigation = [
    { name: 'Dashboard', href: '/', icon: LayoutDashboard },
    { name: 'Facilities', href: '/facilities', icon: Building2 },
    { name: 'Map View', href: '/map', icon: Map },
    { name: 'Clusters', href: '/clusters', icon: Network },
    { name: 'Top Leads', href: '/leads', icon: Zap },
    { name: 'Email Generator', href: '/email-generator', icon: Mail },
    { name: 'Discovery', href: '/discovery', icon: Search },
  ];

  const isActive = (href) => {
    if (href === '/') return location.pathname === '/';
    return location.pathname.startsWith(href);
  };

  const NavLinks = ({ onClickItem }) => (
    <>
      {navigation.map((item) => {
        const Icon = item.icon;
        const active = isActive(item.href);
        return (
          <Link
            key={item.name}
            to={item.href}
            onClick={() => onClickItem && onClickItem()}
            className={`flex items-center gap-3 px-4 py-3 rounded-md text-sm font-medium transition-colors ${
              active
                ? 'bg-accent text-accent-foreground'
                : 'text-muted-foreground hover:bg-muted hover:text-foreground'
            }`}
            data-testid={`nav-${item.name.toLowerCase().replace(' ', '-')}`}
          >
            <Icon className="h-5 w-5" strokeWidth={1.5} />
            <span>{item.name}</span>
          </Link>
        );
      })}
    </>
  );

  return (
    <div className="min-h-screen bg-background">
      {/* Desktop Sidebar */}
      <aside className="hidden lg:fixed lg:inset-y-0 lg:flex lg:w-64 lg:flex-col border-r border-border bg-white">
        <div className="flex flex-col flex-grow pt-6 pb-4 overflow-y-auto">
          <div className="flex items-center flex-shrink-0 px-6 mb-8">
            <div className="flex items-center gap-2">
              <div className="w-10 h-10 rounded-md bg-gradient-to-br from-accent to-blue-500 flex items-center justify-center">
                <Zap className="h-6 w-6 text-white" strokeWidth={2.5} />
              </div>
              <div>
                <h1 className="text-xl font-bold font-heading text-primary">RAD</h1>
                <p className="text-xs text-muted-foreground">Renewable Discovery</p>
              </div>
            </div>
          </div>
          <nav className="flex-1 px-4 space-y-1">
            <NavLinks />
          </nav>
        </div>
      </aside>

      {/* Mobile Header */}
      <div className="lg:hidden sticky top-0 z-40 flex items-center gap-x-6 bg-white px-4 py-4 shadow-sm border-b border-border">
        <Sheet open={open} onOpenChange={setOpen}>
          <SheetTrigger asChild>
            <Button variant="ghost" size="icon" data-testid="mobile-menu-trigger">
              <Menu className="h-6 w-6" />
            </Button>
          </SheetTrigger>
          <SheetContent side="left" className="w-64 p-0">
            <div className="flex flex-col h-full pt-6">
              <div className="flex items-center flex-shrink-0 px-6 mb-8">
                <div className="flex items-center gap-2">
                  <div className="w-10 h-10 rounded-md bg-gradient-to-br from-accent to-blue-500 flex items-center justify-center">
                    <Zap className="h-6 w-6 text-white" strokeWidth={2.5} />
                  </div>
                  <div>
                    <h1 className="text-xl font-bold font-heading text-primary">RAD</h1>
                    <p className="text-xs text-muted-foreground">Renewable Discovery</p>
                  </div>
                </div>
              </div>
              <nav className="flex-1 px-4 space-y-1">
                <NavLinks onClickItem={() => setOpen(false)} />
              </nav>
            </div>
          </SheetContent>
        </Sheet>
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-md bg-gradient-to-br from-accent to-blue-500 flex items-center justify-center">
            <Zap className="h-5 w-5 text-white" strokeWidth={2.5} />
          </div>
          <h1 className="text-lg font-bold font-heading text-primary">RAD</h1>
        </div>
      </div>

      {/* Main Content */}
      <div className="lg:pl-64">
        <main className="p-6 md:p-8 lg:p-10">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default Layout;