import React from 'react';
import { Button, Select } from 'antd';
import './Header.css';

const Header = () => (
  <div className="header-bar">
    <div className="header-title">Home</div>
    <div className="header-actions">
      <Select defaultValue="2025" style={{ width: 100, marginRight: 16 }}>
        <Select.Option value="2025">2025</Select.Option>
        <Select.Option value="2024">2024</Select.Option>
      </Select>
      <Button shape="circle" icon={<span role="img" aria-label="theme">🌙</span>} />
    </div>
  </div>
);

export default Header; 