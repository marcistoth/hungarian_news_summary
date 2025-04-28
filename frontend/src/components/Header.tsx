import React from 'react';

const Header: React.FC = () => {
  return (
    <header className="text-center mb-12 md:mb-16 pt-8 pb-8 border-b-2 border-primary-light/50">
      {/* Optional: Add a subtle logo or icon here */}
      <h1 className="text-4xl sm:text-5xl md:text-6xl font-bold text-primary-dark mb-4 tracking-tight">
        Mai Hírek <span className="text-primary">Összefoglaló</span>
      </h1>
      <p className="text-lg text-text-light max-w-2xl mx-auto">
        A legfrissebb hírek esszenciája, letisztult formában a gyors tájékozódáshoz.
      </p>
    </header>
  );
};

export default Header;