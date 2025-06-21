import React from 'react';
import { Menu } from 'antd';
import { HomeOutlined, TrophyOutlined, TeamOutlined, CarOutlined, SettingOutlined, DashboardOutlined, FlagOutlined } from '@ant-design/icons';
import { useTheme } from '../contexts/ThemeContext';
import './Sidebar.css';

const items = [
  { key: 'home', icon: <HomeOutlined />, label: 'Home' },
  { key: 'schedule', icon: <DashboardOutlined />, label: 'Schedule' },
  { key: 'results', icon: <FlagOutlined />, label: 'Results' },
  { key: 'driver-standings', icon: <TrophyOutlined />, label: 'Driver Standings' },
  { key: 'constructor-standings', icon: <TeamOutlined />, label: 'Constructor Standings' },
  { key: 'teams', icon: <CarOutlined />, label: 'Teams' },
  { key: 'tech-updates', icon: <SettingOutlined />, label: 'Tech Updates' },
];

const Sidebar = ({ activeTab = 'home', onTabChange }) => {
  const { isDarkMode } = useTheme();

  const handleMenuClick = ({ key }) => {
    if (onTabChange) {
      onTabChange(key);
    }
  };

  return (
    <div className="sidebar">
      <div
        className="logo"
        style={{ color: isDarkMode ? '#fff' : '#333' }}
      >
        Formula 1 Dashboard
      </div>
      <Menu
        theme="dark"
        mode="inline"
        selectedKeys={[activeTab]}
        items={items}
        onClick={handleMenuClick}
      />
    </div>
  );
};

export default Sidebar; 