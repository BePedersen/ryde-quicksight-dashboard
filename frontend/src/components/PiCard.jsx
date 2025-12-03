import React, { useState } from 'react'
import { updatePiConfig, restartPiService } from '../api'

export default function PiCard({ pi, cities, onRefresh }) {
  const [editing, setEditing] = useState(false)
  const [loading, setLoading] = useState(false)
  const [city, setCity] = useState(pi.city || '')
  const [mode, setMode] = useState(pi.dashboard_mode || 'operations')
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(null)

  const handleSave = async () => {
    setLoading(true)
    setError(null)
    setSuccess(null)

    try {
      await updatePiConfig(pi.id, {
        city,
        dashboard_mode: mode,
      })
      setSuccess('Configuration updated!')
      setEditing(false)
      setTimeout(() => {
        setSuccess(null)
        onRefresh?.()
      }, 2000)
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to update config')
    } finally {
      setLoading(false)
    }
  }

  const handleRestart = async () => {
    if (!confirm('Restart service on this Pi?')) return

    setLoading(true)
    setError(null)

    try {
      await restartPiService(pi.id)
      setSuccess('Service restarted!')
      setTimeout(() => {
        setSuccess(null)
        onRefresh?.()
      }, 2000)
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to restart service')
    } finally {
      setLoading(false)
    }
  }

  const statusColor = {
    'active': 'bg-green-100 text-green-800',
    'inactive': 'bg-red-100 text-red-800',
    'unknown': 'bg-gray-100 text-gray-800',
    'offline': 'bg-red-100 text-red-800',
    'error': 'bg-red-100 text-red-800',
  }

  const currentStatus = pi.last_status || 'unknown'
  const statusClass = statusColor[currentStatus] || statusColor['unknown']

  return (
    <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="text-lg font-bold text-gray-800">{pi.name}</h3>
          <p className="text-sm text-gray-500">{pi.ip}</p>
        </div>
        <span className={`px-3 py-1 rounded-full text-xs font-semibold ${statusClass}`}>
          {currentStatus}
        </span>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-100 text-red-700 rounded text-sm">
          {error}
        </div>
      )}

      {success && (
        <div className="mb-4 p-3 bg-green-100 text-green-700 rounded text-sm">
          {success}
        </div>
      )}

      {!editing ? (
        <div>
          <div className="space-y-2 mb-4">
            <div>
              <label className="text-xs font-semibold text-gray-600">CITY</label>
              <p className="text-lg text-gray-800">{pi.city || 'Not set'}</p>
            </div>
            <div>
              <label className="text-xs font-semibold text-gray-600">MODE</label>
              <p className="text-lg text-gray-800">{pi.dashboard_mode || 'operations'}</p>
            </div>
          </div>

          <div className="flex gap-2">
            <button
              onClick={() => setEditing(true)}
              className="flex-1 px-3 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 text-sm font-semibold disabled:opacity-50"
              disabled={loading}
            >
              Edit
            </button>
            <button
              onClick={handleRestart}
              className="flex-1 px-3 py-2 bg-orange-500 text-white rounded hover:bg-orange-600 text-sm font-semibold disabled:opacity-50"
              disabled={loading}
            >
              Restart
            </button>
          </div>
        </div>
      ) : (
        <div>
          <div className="space-y-3 mb-4">
            <div>
              <label className="block text-xs font-semibold text-gray-600 mb-1">
                CITY
              </label>
              <select
                value={city}
                onChange={(e) => setCity(e.target.value)}
                className="w-full px-2 py-2 border border-gray-300 rounded text-sm"
              >
                <option value="">Select city...</option>
                {cities.map((c) => (
                  <option key={c} value={c}>
                    {c}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-gray-600 mb-1">
                MODE
              </label>
              <select
                value={mode}
                onChange={(e) => setMode(e.target.value)}
                className="w-full px-2 py-2 border border-gray-300 rounded text-sm"
              >
                <option value="operations">Operations</option>
                <option value="mechanics">Mechanics</option>
              </select>
            </div>
          </div>

          <div className="flex gap-2">
            <button
              onClick={handleSave}
              className="flex-1 px-3 py-2 bg-green-500 text-white rounded hover:bg-green-600 text-sm font-semibold disabled:opacity-50"
              disabled={loading}
            >
              {loading ? 'Saving...' : 'Save'}
            </button>
            <button
              onClick={() => {
                setEditing(false)
                setCity(pi.city || '')
                setMode(pi.dashboard_mode || 'operations')
              }}
              className="flex-1 px-3 py-2 bg-gray-400 text-white rounded hover:bg-gray-500 text-sm font-semibold disabled:opacity-50"
              disabled={loading}
            >
              Cancel
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
