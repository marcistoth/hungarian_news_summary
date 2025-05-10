import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import logo from '../assets/news-summary-logo.png';
import { useLanguage } from '../contexts/LanguageContext';
import LanguageSwitcher from './LanguageSwitcher';

const Header = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const location = useLocation();
  const { t } = useLanguage();
  
  const toggleMenu = () => setIsMenuOpen(!isMenuOpen);
  
  return (
    <header className="w-full py-4 mb-8">
      <div className="flex justify-between items-center">
        {/* Logo and site title */}
        <Link to="/" className="flex items-center">
          <img src={logo} alt="Magyar Hírek Összefoglaló" className="h-10 w-auto mr-2" />
          <h1 className="text-xl md:text-2xl font-bold text-primary hidden sm:block">
            {t('home.title')}
          </h1>
        </Link>
        
        {/* Desktop navigation - all in one line */}
        <div className="hidden md:flex items-center space-x-6">
          <NavLink to="/" isActive={location.pathname === '/'}>
            {t('nav.home')}
          </NavLink>
          <NavLink to="/analysis" isActive={location.pathname === '/analysis'}>
            {t('nav.analysis')}
          </NavLink>
          <NavLink to="/about" isActive={location.pathname === '/about'}>
            {t('nav.about')}
          </NavLink>
          
          {/* Language switcher inline with nav */}
          <LanguageSwitcher />
        </div>
        
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
                {t('nav.home')}
              </Link>
            </li>
            <li>
              <Link 
                to="/analysis" 
                className={`block p-2 rounded ${location.pathname === '/analysis' ? 'bg-primary text-text-on-primary' : 'hover:bg-secondary'}`}
                onClick={() => setIsMenuOpen(false)}
              >
                {t('nav.analysis')}
              </Link>
            </li>
            <li>
              <Link 
                to="/about" 
                className={`block p-2 rounded ${location.pathname === '/about' ? 'bg-primary text-text-on-primary' : 'hover:bg-secondary'}`}
                onClick={() => setIsMenuOpen(false)}
              >
                {t('nav.about')}
              </Link>
            </li>
            {/* Add language switcher for mobile */}
            <li className="pt-2 border-t border-gray-200">
              <div className="flex justify-center">
                <LanguageSwitcher />
              </div>
            </li>
          </ul>
        </nav>
      )}
    </header>
  );
};

// Helper component for nav links
interface NavLinkProps {
  children: React.ReactNode;
  to: string;
  isActive: boolean;
}

const NavLink: React.FC<NavLinkProps> = ({ children, to, isActive }) => (
  <Link
    to={to}
    className={`font-medium transition-colors hover:text-primary ${
      isActive ? 'text-primary' : 'text-text-light'
    }`}
  >
    {children}
  </Link>
);

export default Header;