import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import logo from '../assets/news-summary-logo.png';

const Header = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const location = useLocation();
  
  const toggleMenu = () => setIsMenuOpen(!isMenuOpen);
  
  return (
    <header className="w-full py-4 mb-8">
      <div className="flex justify-between items-center">
        {/* Logo and site title */}
        <Link to="/" className="flex items-center">
          <img src={logo} alt="Magyar Hírek Összefoglaló" className="h-12 w-auto mr-3" />
          <h1 className="text-2xl md:text-3xl font-bold text-primary">
            Magyar Hírek Összefoglaló
          </h1>
        </Link>
        
        {/* Mobile menu button */}
        <button 
          className="md:hidden text-text-light hover:text-primary p-2"
          onClick={toggleMenu}
          aria-label="Toggle menu"
        >
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" className="h-6 w-6">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16m-7 6h7" />
          </svg>
        </button>
        
        {/* Desktop navigation */}
        <nav className="hidden md:flex space-x-6">
          <NavLink to="/" isActive={location.pathname === '/'}>
            Főoldal
          </NavLink>
          <NavLink to="/analysis" isActive={location.pathname === '/analysis'}>
            Elemzés
          </NavLink>
          <NavLink to="/about" isActive={location.pathname === '/about'}>
            A Projektről
          </NavLink>
        </nav>
      </div>
      
      {/* Mobile navigation */}
      {isMenuOpen && (
        <nav className="md:hidden mt-4 p-4 bg-background-alt rounded-lg shadow-md">
          <ul className="space-y-3">
            <li>
              <Link 
                to="/" 
                className={`block p-2 rounded ${location.pathname === '/' ? 'bg-primary text-text-on-primary' : 'hover:bg-secondary'}`}
                onClick={() => setIsMenuOpen(false)}
              >
                Főoldal
              </Link>
            </li>
            <li>
              <Link 
                to="/analysis" 
                className={`block p-2 rounded ${location.pathname === '/analysis' ? 'bg-primary text-text-on-primary' : 'hover:bg-secondary'}`}
                onClick={() => setIsMenuOpen(false)}
              >
                Elemzés
              </Link>
            </li>
            <li>
              <Link 
                to="/about" 
                className={`block p-2 rounded ${location.pathname === '/about' ? 'bg-primary text-text-on-primary' : 'hover:bg-secondary'}`}
                onClick={() => setIsMenuOpen(false)}
              >
                A Projektről
              </Link>
            </li>
          </ul>
        </nav>
      )}
    </header>
  );
};

// Helper component for nav links
interface NavLinkProps {
  to: string;
  isActive: boolean;
  children: React.ReactNode;
}

const NavLink = ({ to, isActive, children }: NavLinkProps) => (
  <Link 
    to={to} 
    className={`px-3 py-2 rounded-md transition-colors ${
      isActive 
        ? 'bg-primary text-text-on-primary font-medium' 
        : 'text-text-light hover:text-primary hover:bg-secondary-light'
    }`}
  >
    {children}
  </Link>
);

export default Header;