import React from 'react';
import { Table } from 'antd';

const StandingsTable = ({ title, data }) => {
  const columns = [
    { title: 'POS.', dataIndex: 'pos', key: 'pos', width: 60 },
    { title: 'DRIVER/CONSTRUCTOR', dataIndex: 'name', key: 'name' },
    { title: 'POINTS', dataIndex: 'points', key: 'points', width: 80 },
    { title: 'EVO.', dataIndex: 'evo', key: 'evo', width: 80 },
  ];
  return (
    <div style={{ marginBottom: 16 }}>
      <div style={{ color: '#fff', fontWeight: 'bold', marginBottom: 8 }}>{title}</div>
      <Table columns={columns} dataSource={data} pagination={false} size="small" rowKey="pos" style={{ background: '#181c2f' }} />
    </div>
  );
};

export default StandingsTable; 