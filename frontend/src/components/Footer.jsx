import React from 'react';
import '../style/Footer.css';

const Footer = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="footer">
      <p>© {currentYear} - Page under AIM Lab</p>
    </footer>
  );
};

export default Footer;
