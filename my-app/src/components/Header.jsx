import React from 'react';
import { Select } from 'antd';
import { useTheme } from '../contexts/ThemeContext';
import './Header.css';

const Header = () => {
  const { isDarkMode, toggleTheme } = useTheme();

  return (
    <div className="header-bar">
      <div className="header-title">Home</div>
      <div className="header-actions">
        <Select defaultValue="2025" style={{ width: 100, marginRight: 16 }}>
          <Select.Option value="2025">2025</Select.Option>
          <Select.Option value="2024">2024</Select.Option>
        </Select>

        {/* 现代化的主题切换按钮 */}
        <div className="theme-toggle" onClick={toggleTheme}>
          <div className={`theme-toggle-track ${isDarkMode ? 'dark' : 'light'}`}>
            <div className={`theme-toggle-thumb ${isDarkMode ? 'dark' : 'light'}`}>
              <span className="theme-icon">
                {isDarkMode ? '🌙' : '☀️'}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Header; 