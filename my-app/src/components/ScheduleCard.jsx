import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Timeline, Spin, Typography, Tag } from 'antd';
import { ClockCircleOutlined, EnvironmentOutlined } from '@ant-design/icons';
import { getRaceWeekendSchedule, getCircuitInfo } from '../api';
import './ScheduleCard.css';

const { Title, Text } = Typography;

const ScheduleCard = ({ year }) => {
  const [schedule, setSchedule] = useState(null);
  const [circuitInfo, setCircuitInfo] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [scheduleResponse, circuitResponse] = await Promise.all([
          getRaceWeekendSchedule(year),
          getCircuitInfo(year)
        ]);
        setSchedule(scheduleResponse.data);
        setCircuitInfo(circuitResponse.data);
      } catch (error) {
        console.error('Error fetching schedule data:', error);
      } finally {
        setLoading(false);
      }
    };

    if (year) {
      fetchData();
    }
  }, [year]);

  const formatTimeWithTimezone = (datetimeStr) => {
    if (!datetimeStr) return '';

    const date = new Date(datetimeStr);
    const userTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone;

    return date.toLocaleString('en-US', {
      timeZone: userTimezone,
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      hour12: false
    });
  };

  const getSessionColor = (sessionCode, status) => {
    const colors = {
      'FP1': status === 'live' ? '#87d068' : '#52c41a',
      'FP2': status === 'live' ? '#87d068' : '#52c41a',
      'FP3': status === 'live' ? '#87d068' : '#52c41a',
      'Q': status === 'live' ? '#ffa940' : '#fa8c16',
      'R': status === 'live' ? '#ff7875' : '#ff4d4f'
    };
    return colors[sessionCode] || '#1890ff';
  };

  const getSessionStatusTag = (status) => {
    const statusConfig = {
      'upcoming': { text: 'Upcoming', color: 'blue' },
      'live': { text: 'Live Now', color: 'red' },
      'completed': { text: 'Completed', color: 'green' }
    };
    return statusConfig[status] || statusConfig['upcoming'];
  };

  if (loading) {
    return (
      <Card
        className="schedule-card"
        style={{ minHeight: 300 }}
      >
        <div style={{ textAlign: 'center', padding: '50px 0' }}>
          <Spin size="large" />
          <div style={{ marginTop: 16, color: '#fff' }}>Loading race information...</div>
        </div>
      </Card>
    );
  }

  if (!schedule || !schedule.race_info) {
    return (
      <Card className="schedule-card">
        <div style={{ textAlign: 'center', padding: '50px 0', color: '#fff' }}>
          No race information available
        </div>
      </Card>
    );
  }

  return (
    <Card
      className="schedule-card"
      title={
        <div className="schedule-header">
          <Title level={4} style={{ color: '#fff', margin: 0 }}>
            {schedule.race_info.race_name}
          </Title>
          <div style={{ marginTop: 4 }}>
            <EnvironmentOutlined style={{ color: '#8c8c8c', marginRight: 4 }} />
            <Text style={{ color: '#8c8c8c' }}>
              {schedule.race_info.location}, {schedule.race_info.country}
            </Text>
          </div>
        </div>
      }
    >
      <Row gutter={24} style={{ minHeight: 250 }}>
        {/* 左侧：时间表 */}
        <Col span={14}>
          <div className="schedule-timeline">
            <Title level={5} style={{ color: '#fff', marginBottom: 16 }}>
              <ClockCircleOutlined style={{ marginRight: 8 }} />
              Race Weekend Schedule
            </Title>
            <Timeline>
              {schedule.sessions && schedule.sessions.map((session, index) => (
                <Timeline.Item
                  key={index}
                  color={getSessionColor(session.code, session.status)}
                  dot={
                    session.status === 'live' ? (
                      <div
                        style={{
                          width: '12px',
                          height: '12px',
                          borderRadius: '50%',
                          backgroundColor: getSessionColor(session.code, session.status),
                          border: '2px solid #fff',
                          animation: 'pulse 2s infinite'
                        }}
                      />
                    ) : session.status === 'upcoming' ? (
                      <div
                        style={{
                          width: '12px',
                          height: '12px',
                          borderRadius: '50%',
                          backgroundColor: 'transparent',
                          border: `2px solid ${getSessionColor(session.code, session.status)}`,
                          position: 'relative'
                        }}
                      />
                    ) : undefined
                  }
                >
                  <div className="session-item">
                    <div className="session-header">
                      <Text strong style={{ color: '#fff', fontSize: '16px' }}>
                        {session.name}
                      </Text>
                      <Tag
                        color={getSessionColor(session.code, session.status)}
                        style={{ marginLeft: 8 }}
                      >
                        {session.code}
                      </Tag>
                      <Tag
                        color={getSessionStatusTag(session.status).color}
                        style={{ marginLeft: 4 }}
                      >
                        {getSessionStatusTag(session.status).text}
                      </Tag>
                    </div>
                    <Text style={{ color: '#8c8c8c', fontSize: '14px' }}>
                      {session.status === 'live' ? (
                        <>
                          {formatTimeWithTimezone(session.datetime)} - {formatTimeWithTimezone(session.end_datetime)}
                        </>
                      ) : (
                        formatTimeWithTimezone(session.datetime)
                      )}
                    </Text>
                  </div>
                </Timeline.Item>
              ))}
            </Timeline>
          </div>
        </Col>

        {/* 右侧：赛道图片 */}
        <Col span={10}>
          <div className="circuit-section">
            <Title level={5} style={{ color: '#fff', marginBottom: 16 }}>
              Circuit Layout
            </Title>
            {circuitInfo?.image_url ? (
              <div className="circuit-image-container">
                <img
                  src={circuitInfo.image_url}
                  alt={`${circuitInfo.name} Circuit`}
                  className="circuit-image"
                  onError={(e) => {
                    e.target.style.display = 'none';
                    e.target.nextSibling.style.display = 'block';
                  }}
                />
                <div className="circuit-fallback" style={{ display: 'none' }}>
                  <div className="circuit-placeholder">
                    <EnvironmentOutlined style={{ fontSize: '48px', color: '#8c8c8c' }} />
                    <Text style={{ color: '#8c8c8c', marginTop: 8, display: 'block' }}>
                      {circuitInfo.name || 'Circuit Image'}
                    </Text>
                  </div>
                </div>
              </div>
            ) : (
              <div className="circuit-placeholder">
                <EnvironmentOutlined style={{ fontSize: '48px', color: '#8c8c8c' }} />
                <Text style={{ color: '#8c8c8c', marginTop: 8, display: 'block' }}>
                  {schedule.circuit?.name || 'Circuit Image Unavailable'}
                </Text>
              </div>
            )}

            {circuitInfo && (
              <div className="circuit-info" style={{ marginTop: 16 }}>
                <Text style={{ color: '#8c8c8c', fontSize: '12px', display: 'block' }}>
                  Circuit: {circuitInfo.name || schedule.circuit?.name}
                </Text>
                <Text style={{ color: '#8c8c8c', fontSize: '12px', display: 'block' }}>
                  Location: {circuitInfo.location}, {circuitInfo.country}
                </Text>
              </div>
            )}
          </div>
        </Col>
      </Row>
    </Card>
  );
};

export default ScheduleCard; 