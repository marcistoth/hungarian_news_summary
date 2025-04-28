// filepath: frontend/src/components/Footer.tsx
import React from 'react';

const Footer: React.FC = () => {
  return (
    <footer className="text-center mt-16 pt-6 border-t border-gray-200 text-text-muted text-sm">
      <p>&copy; {new Date().getFullYear()} MagyarMa Hírek</p>
    </footer>
  );
};

export default Footer;