import { useEffect, useRef, useState } from "react";
import { AppIcon } from "./AppIcon";

type User = { email: string; full_name: string };

export function UserMenu({ user, onLogout }: { user: User; onLogout: () => void }) {
  const [open, setOpen] = useState(false);
  const rootRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const close = (event: MouseEvent) => {
      if (!rootRef.current?.contains(event.target as Node)) setOpen(false);
    };
    document.addEventListener("mousedown", close);
    return () => document.removeEventListener("mousedown", close);
  }, []);

  return <div className="user-menu-popover" ref={rootRef}>
    <button className="avatar" aria-label="Open account menu" aria-expanded={open} onClick={() => setOpen((value) => !value)}>{user.full_name.slice(0, 2).toUpperCase()}</button>
    {open && <div className="user-menu-panel" role="menu">
      <strong>{user.full_name}</strong>
      <small>{user.email}</small>
      <button role="menuitem" onClick={onLogout}><AppIcon name="logout" /> Log out</button>
    </div>}
  </div>;
}
