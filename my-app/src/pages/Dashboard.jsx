import React, { useEffect, useState } from 'react';
import { Row, Col } from 'antd';
import Sidebar from '../components/Sidebar';
import Header from '../components/Header';
import DashboardCard from '../components/DashboardCard';
import ScheduleCard from '../components/ScheduleCard';
import StandingsTable from '../components/StandingsTable';
import Results from './Results';
import { getDriverStandings, getConstructorStandings, getNextRace, getAvailableYears } from '../api';
import './Dashboard.css';

const Dashboard = () => {
  const [drivers, setDrivers] = useState([]);
  const [constructors, setConstructors] = useState([]);
  const [nextRace, setNextRace] = useState(null);
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear());
  const [availableYears, setAvailableYears] = useState([]);
  const [activeTab, setActiveTab] = useState('home');

  useEffect(() => {
    // 获取可用年份
    getAvailableYears().then(res => {
      const years = res.data;
      setAvailableYears(years);
      if (years.length > 0) {
        setSelectedYear(Math.max(...years));
      }
    });
  }, []);

  useEffect(() => {
    if (selectedYear && activeTab === 'home') {
      // 获取车手和车队积分榜
      getDriverStandings().then(res => setDrivers(res.data));
      getConstructorStandings().then(res => setConstructors(res.data));
      // 获取下一场比赛信息
      getNextRace(selectedYear).then(res => setNextRace(res.data));
    }
  }, [selectedYear, activeTab]);

  const renderContent = () => {
    switch (activeTab) {
      case 'results':
        return <Results />;
      case 'home':
      default:
        return (
          <div className="dashboard-content">
            <Row gutter={16}>
              <Col span={8}>
                <DashboardCard
                  title={nextRace ? `${nextRace.raceName}: Next Session` : 'Loading...'}
                  value={nextRace ? nextRace.nextSession : 'Loading...'}
                />
              </Col>
              <Col span={8}>
                <DashboardCard
                  title={`${selectedYear} Fastest Pit Stop`}
                  value="Loading..."
                />
              </Col>
            </Row>

            {/* 新的Schedule卡片 - 占据整行 */}
            <Row gutter={16} style={{ marginTop: 24 }}>
              <Col span={24}>
                <ScheduleCard year={selectedYear} />
              </Col>
            </Row>

            <Row gutter={16} style={{ marginTop: 24 }}>
              <Col span={12}>
                <StandingsTable title={`${selectedYear} Driver Standings`} data={drivers} />
              </Col>
              <Col span={12}>
                <StandingsTable title={`${selectedYear} Constructor Standings`} data={constructors} />
              </Col>
            </Row>
          </div>
        );
    }
  };

  return (
    <div className="dashboard-layout">
      <Sidebar activeTab={activeTab} onTabChange={setActiveTab} />
      <div className="dashboard-main">
        <Header />
        {renderContent()}
      </div>
    </div>
  );
};

export default Dashboard; 