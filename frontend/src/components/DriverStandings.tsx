import React, { useState, useEffect } from 'react'

interface Driver {
  pos: number
  name: string
  points: number
  evo: number
}

interface DriverStandingsProps {
  year: number
}

export const DriverStandings: React.FC<DriverStandingsProps> = ({ year }) => {
  const [drivers, setDrivers] = useState<Driver[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(true)
    fetch(`http://localhost:8000/api/driver-standings?year=${year}`)
      .then(response => response.json())
      .then(data => {
        setDrivers(data)
        setLoading(false)
      })
      .catch(error => {
        console.error('Error fetching driver standings:', error)
        setLoading(false)
      })
  }, [year])

  if (loading) return <div>Loading driver standings...</div>

  return (
    <div className="standings-container">
      <h2>Driver Standings {year}</h2>
      <table className="standings-table">
        <thead>
          <tr>
            <th>POS</th>
            <th>DRIVER</th>
            <th>POINTS</th>
            <th>EVO</th>
          </tr>
        </thead>
        <tbody>
          {drivers.map(driver => (
            <tr key={driver.pos}>
              <td>{driver.pos}</td>
              <td>{driver.name}</td>
              <td>{driver.points}</td>
              <td>{driver.evo}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
} 