import React, { useEffect, useState } from 'react';
import { Row, Col } from 'antd';
import Sidebar from '../components/Sidebar';
import Header from '../components/Header';
import DashboardCard from '../components/DashboardCard';
import StandingsTable from '../components/StandingsTable';
import './Dashboard.css';
import { getDriverStandings, getConstructorStandings } from '../api';

const Dashboard = () => {
  // mock 数据
  const mockDashboard = {
    practice: 'Spain: Practice 1',
    schedule: 'Spain',
    fastestPitStop: '2.00 s',
  };
  const mockDrivers = [
    { pos: 1, name: 'Piastri', points: 161, evo: 0 },
    { pos: 2, name: 'Norris', points: 158, evo: -3 },
    { pos: 3, name: 'Verstappen', points: 136, evo: -2 },
    { pos: 4, name: 'Russell', points: 99, evo: -62 },
    { pos: 5, name: 'Leclerc', points: 79, evo: -82 },
    { pos: 6, name: 'Hamilton', points: 63, evo: -98 },
    { pos: 7, name: 'Antonelli', points: 48, evo: -113 },
    { pos: 8, name: 'Albon', points: 42, evo: -119 },
    { pos: 9, name: 'Ocon', points: 20, evo: -141 },
    { pos: 10, name: 'Hadjar', points: 15, evo: -146 },
  ];
  const mockConstructors = [
    { pos: 1, name: 'McLaren', points: 319, evo: 0 },
    { pos: 2, name: 'Mercedes', points: 147, evo: -172 },
    { pos: 3, name: 'Red Bull Racing', points: 143, evo: -176 },
    { pos: 4, name: 'Ferrari', points: 142, evo: -177 },
    { pos: 5, name: 'Williams', points: 54, evo: -265 },
    { pos: 6, name: 'Haas', points: 26, evo: -293 },
    { pos: 7, name: 'RB', points: 22, evo: -297 },
    { pos: 8, name: 'Aston Martin', points: 14, evo: -305 },
    { pos: 9, name: 'Alpine', points: 7, evo: -312 },
    { pos: 10, name: 'Kick Sauber', points: 6, evo: -313 },
  ];

  const [dashboard, setDashboard] = useState({});
  const [drivers, setDrivers] = useState([]);
  const [constructors, setConstructors] = useState([]);

  useEffect(() => {
    setDashboard(mockDashboard);
    setDrivers(mockDrivers);
    setConstructors(mockConstructors);
  }, []);

  useEffect(() => {
    getDriverStandings().then(res => setDrivers(res.data));
    getConstructorStandings().then(res => setConstructors(res.data));
  }, []);

  return (
    <div className="dashboard-layout">
      <Sidebar />
      <div className="dashboard-main">
        <Header />
        <div className="dashboard-content">
          <Row gutter={16}>
            <Col span={8}>
              <DashboardCard title={dashboard.practice || ''} value="02:09:47:01" />
            </Col>
            <Col span={8}>
              <DashboardCard title="2025 Schedule" value={dashboard.schedule || ''} />
            </Col>
            <Col span={8}>
              <DashboardCard title="2025 Fastest Pit Stop" value={dashboard.fastestPitStop || ''} />
            </Col>
          </Row>
          {/* 其他卡片可继续添加 */}
          <Row gutter={16} style={{ marginTop: 24 }}>
            <Col span={12}>
              <StandingsTable title="2025 Driver Standings" data={drivers} />
            </Col>
            <Col span={12}>
              <StandingsTable title="2025 Constructor Standings" data={constructors} />
            </Col>
          </Row>
        </div>
      </div>
    </div>
  );
};

export default Dashboard; 