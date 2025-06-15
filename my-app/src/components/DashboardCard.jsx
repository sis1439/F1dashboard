import React from 'react';
import { Card } from 'antd';

const DashboardCard = ({ title, value, extra, children }) => (
  <Card
    title={title}
    extra={extra}
    style={{ marginBottom: 16, background: '#181c2f', color: '#fff' }}
    headStyle={{ color: '#fff', background: '#181c2f' }}
    bodyStyle={{ color: '#fff' }}
  >
    <div style={{ fontSize: 28, fontWeight: 'bold' }}>{value}</div>
    {children}
  </Card>
);

export default DashboardCard; 