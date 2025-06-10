import React, { useState, useEffect } from 'react'
import './App.css'
import { DriverStandings } from './components/DriverStandings'
import { ConstructorStandings } from './components/ConstructorStandings'

function App() {
  const [selectedYear, setSelectedYear] = useState<number>(new Date().getFullYear())
  const [availableYears, setAvailableYears] = useState<number[]>([])

  useEffect(() => {
    // Fetch available years list
    fetch('http://localhost:8000/api/available-years')
      .then(response => response.json())
      .then(years => {
        setAvailableYears(years)
        // Select the latest year by default
        if (years.length > 0) {
          setSelectedYear(Math.max(...years))
        }
      })
  }, [])

  return (
    <div className="app-container">
      <div className="header">
        <h1>F1 Dashboard</h1>
        <div className="year-selector">
          <select
            value={selectedYear}
            onChange={(e) => setSelectedYear(Number(e.target.value))}
            className="year-select"
          >
            {availableYears.map(year => (
              <option key={year} value={year}>{year}</option>
            ))}
          </select>
        </div>
      </div>
      <div className="dashboard">
        <DriverStandings year={selectedYear} />
        <ConstructorStandings year={selectedYear} />
      </div>
    </div>
  )
}

export default App 