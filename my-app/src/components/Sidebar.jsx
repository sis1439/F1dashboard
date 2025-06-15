import React from 'react';
import { Menu } from 'antd';
import { HomeOutlined, TrophyOutlined, TeamOutlined, CarOutlined, SettingOutlined, DashboardOutlined } from '@ant-design/icons';
import { useTheme } from '../contexts/ThemeContext';
import './Sidebar.css';

const items = [
  { key: 'home', icon: <HomeOutlined />, label: 'Home' },
  { key: 'schedule', icon: <DashboardOutlined />, label: 'Schedule' },
  { key: 'driver-standings', icon: <TrophyOutlined />, label: 'Driver Standings' },
  { key: 'constructor-standings', icon: <TeamOutlined />, label: 'Constructor Standings' },
  { key: 'teams', icon: <CarOutlined />, label: 'Teams' },
  { key: 'tech-updates', icon: <SettingOutlined />, label: 'Tech Updates' },
];

const Sidebar = () => {
  const { isDarkMode } = useTheme();

  return (
    <div className="sidebar">
      <div
        className="logo"
        style={{ color: isDarkMode ? '#fff' : '#333' }}
      >
        Formula 1 Dashboard
      </div>
      <Menu theme="dark" mode="inline" defaultSelectedKeys={['home']} items={items} />
    </div>
  );
};

export default Sidebar; 