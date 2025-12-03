import React, { useState, useEffect } from 'react'
import { getPis, getCities } from '../api'
import PiCard from './PiCard'

export default function Dashboard() {
  const [pis, setPis] = useState([])
  const [cities, setCities] = useState([])
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)

  useEffect(() => {
    fetchData()
    const interval = setInterval(fetchData, 30000) // Refresh every 30 seconds
    return () => clearInterval(interval)
  }, [])

  const fetchData = async () => {
    try {
      setLoading(true)
      const [pisRes, citiesRes] = await Promise.all([
        getPis(),
        getCities(),
      ])
      setPis(pisRes.data)
      setCities(citiesRes.data.cities || [])
    } catch (err) {
      console.error('Failed to fetch data:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleRefresh = async () => {
    setRefreshing(true)
    await fetchData()
    setRefreshing(false)
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="flex justify-between items-center">
            <h1 className="text-3xl font-bold text-gray-900">
              🖥️ QuickSight Dashboard Manager
            </h1>
            <button
              onClick={handleRefresh}
              disabled={refreshing || loading}
              className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50 font-semibold text-sm"
            >
              {refreshing ? 'Refreshing...' : 'Refresh'}
            </button>
          </div>
          <p className="text-gray-600 text-sm mt-2">
            Manage configurations for {pis.length} Raspberry Pi displays
          </p>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8">
        {loading ? (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
            <p className="text-gray-600 mt-4">Loading Pi configurations...</p>
          </div>
        ) : pis.length === 0 ? (
          <div className="text-center py-12 bg-white rounded-lg shadow">
            <p className="text-gray-600">No Pi configurations found</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {pis.map((pi) => (
              <PiCard
                key={pi.id}
                pi={pi}
                cities={cities}
                onRefresh={handleRefresh}
              />
            ))}
          </div>
        )}
      </main>

      <footer className="bg-white border-t border-gray-200 mt-12 py-6">
        <div className="max-w-7xl mx-auto px-6 text-center text-gray-600 text-sm">
          <p>Ryde QuickSight Dashboard Manager v0.1.0</p>
        </div>
      </footer>
    </div>
  )
}
