import React, { useState, useEffect } from 'react'

interface Constructor {
  pos: number
  name: string
  points: number
  evo: number
}

interface ConstructorStandingsProps {
  year: number
}

export const ConstructorStandings: React.FC<ConstructorStandingsProps> = ({ year }) => {
  const [constructors, setConstructors] = useState<Constructor[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(true)
    fetch(`http://localhost:8000/api/constructor-standings?year=${year}`)
      .then(response => response.json())
      .then(data => {
        setConstructors(data)
        setLoading(false)
      })
      .catch(error => {
        console.error('Error fetching constructor standings:', error)
        setLoading(false)
      })
  }, [year])

  if (loading) return <div>Loading constructor standings...</div>

  return (
    <div className="standings-container">
      <h2>Constructor Standings {year}</h2>
      <table className="standings-table">
        <thead>
          <tr>
            <th>POS</th>
            <th>CONSTRUCTOR</th>
            <th>POINTS</th>
            <th>EVO</th>
          </tr>
        </thead>
        <tbody>
          {constructors.map(constructor => (
            <tr key={constructor.pos}>
              <td>{constructor.pos}</td>
              <td>{constructor.name}</td>
              <td>{constructor.points}</td>
              <td>{constructor.evo}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
} 