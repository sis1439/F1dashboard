import React from 'react';
import { Table } from 'antd';
import { useTheme } from '../contexts/ThemeContext';
import './StandingsTable.css';

const StandingsTable = ({ title, data }) => {
  const { isDarkMode } = useTheme();

  // 根据标题判断是车手还是车队积分榜
  const isDriverStandings = title.toLowerCase().includes('driver');
  const columnTitle = isDriverStandings ? 'DRIVER' : 'CONSTRUCTOR';

  // 格式化 EVO 显示（排名变化）
  const formatEvo = (evo) => {
    if (evo > 0) {
      return <span style={{ color: '#52c41a', fontWeight: 'bold' }}>↑ {evo}</span>; // 绿色箭头，排名上升
    } else if (evo < 0) {
      return <span style={{ color: '#ff4d4f', fontWeight: 'bold' }}>↓ {Math.abs(evo)}</span>; // 红色箭头，排名下降
    } else {
      return <span style={{ color: '#8c8c8c' }}>- 0</span>; // 灰色，无变化
    }
  };

  // 格式化积分变化显示
  const formatPointsChange = (pointsChange) => {
    if (pointsChange > 0) {
      return <span style={{ color: '#52c41a' }}>+{pointsChange}</span>; // 绿色，积分增加
    } else if (pointsChange < 0) {
      return <span style={{ color: '#ff4d4f' }}>{pointsChange}</span>; // 红色，积分减少
    } else {
      return <span style={{ color: '#8c8c8c' }}>0</span>; // 灰色，无变化
    }
  };

  const columns = [
    { title: 'POS.', dataIndex: 'pos', key: 'pos', width: 60 },
    { title: columnTitle, dataIndex: 'name', key: 'name' },
    { title: 'POINTS', dataIndex: 'points', key: 'points', width: 80 },
    {
      title: 'POINTS CHANGE',
      dataIndex: 'points_change',
      key: 'points_change',
      width: 120,
      render: (pointsChange) => formatPointsChange(pointsChange)
    },
    {
      title: 'EVO.',
      dataIndex: 'evo',
      key: 'evo',
      width: 80,
      render: (evo) => formatEvo(evo)
    },
  ];

  return (
    <div className="standings-table-container">
      <div
        className="standings-title"
        style={{
          color: isDarkMode ? '#fff' : '#333'
        }}
      >
        {title}
      </div>
      <Table
        columns={columns}
        dataSource={data}
        pagination={false}
        size="small"
        rowKey="pos"
        className={isDarkMode ? 'dark-table' : 'light-table'}
      />
    </div>
  );
};

export default StandingsTable; 