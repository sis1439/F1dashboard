import React, { useState, useEffect } from 'react';
import { Row, Col, Card, Select, Button, Table, Tag, Spin, message } from 'antd';
import { useTheme } from '../contexts/ThemeContext';
import { getAvailableYears, getRaceSchedule, getRaceResults, getQualifyingResults, getPracticeResults, getAvailableSessions } from '../api';
import './Results.css';

// 在组件外部定义，保证引用稳定，避免在每次渲染时产生新数组对象
export const defaultSessionTypes = [
  { key: 'Practice 1', value: 'FP1', label: 'Practice 1' },
  { key: 'Practice 2', value: 'FP2', label: 'Practice 2' },
  { key: 'Practice 3', value: 'FP3', label: 'Practice 3' },
  { key: 'Qualifying', value: 'Q', label: 'Qualifying' },
  { key: 'Race', value: 'R', label: 'Race' }
];

const { Option } = Select;

const Results = () => {
  const { isDarkMode } = useTheme();
  const [loading, setLoading] = useState(false);
  const [availableYears, setAvailableYears] = useState([]);
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear());
  const [raceSchedule, setRaceSchedule] = useState([]);
  const [selectedRound, setSelectedRound] = useState(null);
  const [sessionType, setSessionType] = useState('Race');
  const [resultsData, setResultsData] = useState([]);
  const [availableSessions, setAvailableSessions] = useState([]);
  const [sessionsLoading, setSessionsLoading] = useState(false);

  // 获取可用年份
  useEffect(() => {
    getAvailableYears().then(res => {
      const years = res.data;
      setAvailableYears(years);
      if (years.length > 0) {
        setSelectedYear(Math.max(...years));
      }
    }).catch(err => {
      console.error('Error fetching available years:', err);
    });
  }, []);

  // 获取赛程
  useEffect(() => {
    if (selectedYear) {
      getRaceSchedule(selectedYear).then(res => {
        setRaceSchedule(res.data);
        if (res.data.length > 0) {
          setSelectedRound(res.data[0].round);
        }
      }).catch(err => {
        console.error('Error fetching race schedule:', err);
      });
    }
  }, [selectedYear]);

  // 获取可用的会话
  const fetchAvailableSessions = React.useCallback(async () => {
    if (!selectedYear || !selectedRound) return;

    setSessionsLoading(true);
    try {
      const response = await getAvailableSessions(selectedYear, selectedRound);
      const sessions = response.data.sessions_available || [];

      // 转换为前端需要的格式
      const formattedSessions = sessions.map(session => ({
        key: session.name,
        value: session.session,
        label: session.name
      }));

      setAvailableSessions(formattedSessions);

      // 如果当前选择的会话不在可用会话中，切换到第一个可用会话
      if (formattedSessions.length > 0) {
        const currentSessionExists = formattedSessions.some(s => s.key === sessionType);
        if (!currentSessionExists) {
          // 优先选择Race，如果没有则选择第一个
          const raceSession = formattedSessions.find(s => s.key === 'Race');
          const defaultSession = raceSession || formattedSessions[0];
          setSessionType(defaultSession.key);
        }
      }
    } catch (error) {
      console.error('Error fetching available sessions:', error);
      // 使用默认会话作为后备
      setAvailableSessions(defaultSessionTypes);
    } finally {
      setSessionsLoading(false);
    }
  }, [selectedYear, selectedRound, sessionType, defaultSessionTypes]);

  // 获取可用会话
  useEffect(() => {
    fetchAvailableSessions();
  }, [fetchAvailableSessions]);

  const fetchResults = React.useCallback(async () => {
    if (!selectedYear || !selectedRound) return;

    setLoading(true);
    try {
      let response;
      // 从可用会话中找到对应的会话值，如果没找到则从默认会话中找
      const allSessions = availableSessions.length > 0 ? availableSessions : defaultSessionTypes;
      const sessionValue = allSessions.find(s => s.key === sessionType)?.value;

      if (sessionType === 'Race') {
        response = await getRaceResults(selectedYear, selectedRound);
        setResultsData(response.data.results || []);
      } else if (sessionType === 'Qualifying') {
        response = await getQualifyingResults(selectedYear, selectedRound);
        setResultsData(response.data || []);
      } else if (sessionType === 'Sprint') {
        // Sprint会话使用practice-results API但数据格式类似race
        response = await getPracticeResults(selectedYear, selectedRound, sessionValue);
        setResultsData(response.data || []);
      } else {
        // 其他会话（练习赛、Sprint Qualifying等）
        response = await getPracticeResults(selectedYear, selectedRound, sessionValue);
        setResultsData(response.data || []);
      }

    } catch (error) {
      console.error('Error fetching results:', error);
      message.error('获取结果数据失败');
      setResultsData([]);
    } finally {
      setLoading(false);
    }
  }, [selectedYear, selectedRound, sessionType, availableSessions, defaultSessionTypes]);

  // 获取结果数据
  useEffect(() => {
    fetchResults();
  }, [fetchResults]);

  // 表格列定义
  const getColumns = () => {
    const baseColumns = [
      {
        title: 'Pos.',
        dataIndex: 'position',
        key: 'position',
        width: 60,
        render: (pos) => pos || 'NC'
      },
      {
        title: 'Driver',
        dataIndex: 'driver',
        key: 'driver',
        width: 150
      },
      {
        title: 'Team',
        dataIndex: 'team',
        key: 'team',
        width: 150,
        render: (team) => <Tag color="blue">{team}</Tag>
      }
    ];

    if (sessionType === 'Race' || sessionType === 'Sprint') {
      return [
        ...baseColumns,
        {
          title: 'Laps',
          dataIndex: 'laps',
          key: 'laps',
          width: 80,
          render: (laps) => laps !== null && laps !== undefined ? laps : '-'
        },
        {
          title: 'Time',
          dataIndex: 'time',
          key: 'time',
          width: 120,
          render: (time) => time || '-'
        },
        {
          title: 'Gap to Leader',
          dataIndex: 'gap',
          key: 'gap',
          width: 120,
          render: (gap, record) => {
            // 第一名不显示gap
            if (record.position === 1) {
              return '-';
            }
            return gap || '-';
          }
        },
        {
          title: sessionType === 'Sprint' ? 'Status' : 'Interval',
          dataIndex: 'status',
          key: 'status',
          width: 100,
          render: (status) => status || '-'
        },
        {
          title: 'Points',
          dataIndex: 'points',
          key: 'points',
          width: 80,
          render: (points) => points || 0
        }
      ];
    } else if (sessionType === 'Qualifying') {
      return [
        ...baseColumns,
        {
          title: 'Q1',
          dataIndex: 'q1',
          key: 'q1',
          width: 100,
          render: (time) => time || '-'
        },
        {
          title: 'Q2',
          dataIndex: 'q2',
          key: 'q2',
          width: 100,
          render: (time) => time || '-'
        },
        {
          title: 'Q3',
          dataIndex: 'q3',
          key: 'q3',
          width: 100,
          render: (time) => time || '-'
        }
      ];
    } else if (sessionType === 'Sprint Qualifying') {
      return [
        ...baseColumns,
        {
          title: 'Laps',
          dataIndex: 'laps',
          key: 'laps',
          width: 80,
          render: (laps) => laps || 0
        },
        {
          title: 'Best Time',
          dataIndex: 'time',
          key: 'time',
          width: 120,
          render: (time) => time || '-'
        },
        {
          title: 'Gap to Fastest',
          dataIndex: 'gap',
          key: 'gap',
          width: 120,
          render: (gap, record) => {
            // 第一名不显示gap
            if (record.position === 1) {
              return '-';
            }
            return gap || '-';
          }
        }
      ];
    } else {
      return [
        ...baseColumns,
        {
          title: 'Laps',
          dataIndex: 'laps',
          key: 'laps',
          width: 80,
          render: (laps) => laps || 0
        },
        {
          title: 'Best Time',
          dataIndex: 'time',
          key: 'time',
          width: 120,
          render: (time) => time || '-'
        },
        {
          title: 'Gap to Fastest',
          dataIndex: 'gap',
          key: 'gap',
          width: 120,
          render: (gap, record) => {
            // 第一名不显示gap
            if (record.position === 1) {
              return '-';
            }
            return gap || '-';
          }
        }
      ];
    }
  };

  const selectedRaceInfo = raceSchedule.find(race => race.round === selectedRound);

  return (
    <div className={`results-page ${isDarkMode ? 'dark' : 'light'}`}>
      <div className="results-header">
        <h1>Results</h1>
      </div>

      {/* 控制面板 */}
      <Card className="results-controls" style={{ marginBottom: 24 }}>
        <Row gutter={16} align="middle">
          <Col span={4}>
            <div className="control-label">Season</div>
            <Select
              style={{ width: '100%' }}
              value={selectedYear}
              onChange={(year) => {
                setSelectedYear(year);
                setResultsData([]);
              }}
            >
              {availableYears.map(year => (
                <Option key={year} value={year}>{year}</Option>
              ))}
            </Select>
          </Col>

          <Col span={8}>
            <div className="control-label">Grand Prix</div>
            <Select
              style={{ width: '100%' }}
              value={selectedRound}
              onChange={(round) => {
                setSelectedRound(round);
                setResultsData([]);
                // 重置会话选择，将在fetchAvailableSessions中自动选择合适的会话
                setAvailableSessions([]);
              }}
              loading={!raceSchedule.length}
            >
              {raceSchedule.map(race => (
                <Option key={race.round} value={race.round}>
                  {race.country} - {race.race_name}
                </Option>
              ))}
            </Select>
          </Col>

          <Col span={12}>
            <div className="control-label">Session</div>
            <div className="session-buttons">
              {sessionsLoading ? (
                <Spin size="small" />
              ) : (
                (availableSessions.length > 0 ? availableSessions : defaultSessionTypes).map(session => (
                  <Button
                    key={session.key}
                    type={sessionType === session.key ? 'primary' : 'default'}
                    onClick={() => {
                      setSessionType(session.key);
                      // 立即清空数据，显示加载状态
                      setResultsData([]);
                    }}
                    className="session-button"
                  >
                    {session.label}
                  </Button>
                ))
              )}
            </div>
          </Col>
        </Row>
      </Card>

      {/* 比赛信息 */}
      {selectedRaceInfo && (
        <Card className="race-info-card" style={{ marginBottom: 24 }}>
          <Row gutter={16}>
            <Col span={8}>
              <div className="info-card">
                <div className="info-title">比赛信息</div>
                <div className="info-content">
                  <div className="winner-name">{selectedRaceInfo.race_name}</div>
                  <div className="winner-time">{selectedRaceInfo.location}</div>
                </div>
              </div>
            </Col>
            <Col span={8}>
              <div className="info-card">
                <div className="info-title">比赛日期</div>
                <div className="info-content">
                  <div className="winner-name">{selectedRaceInfo.date}</div>
                  <div className="winner-time">Round {selectedRaceInfo.round}</div>
                </div>
              </div>
            </Col>
            <Col span={8}>
              <div className="info-card">
                <div className="info-title">当前会话</div>
                <div className="info-content">
                  <div className="winner-name">{sessionType}</div>
                  <div className="winner-time">{selectedYear} 赛季</div>
                </div>
              </div>
            </Col>
          </Row>
        </Card>
      )}

      {/* 结果表格 */}
      <Card className="results-table-card">
        <Spin spinning={loading}>
          <Table
            columns={getColumns()}
            dataSource={resultsData}
            rowKey={(record, index) => `${record.position || index}`}
            pagination={false}
            scroll={{ x: 'max-content' }}
            className="results-table"
            locale={{
              emptyText: loading ? '数据加载中...' : `暂无${sessionType}数据，请尝试其他会话或比赛`
            }}
          />
        </Spin>
      </Card>
    </div>
  );
};

export default Results; 