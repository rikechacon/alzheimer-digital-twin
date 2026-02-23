import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { Layout } from 'antd'
import { Header } from './components/Header'
import { Sidebar } from './components/Sidebar'
import { Dashboard } from './pages/Dashboard'
import { PatientView } from './pages/PatientView'
import { InterventionPlanner } from './pages/InterventionPlanner'
import { Simulations } from './pages/Simulations'
import { Settings } from './pages/Settings'
import './App.css'

const { Content } = Layout

function App() {
  const [collapsed, setCollapsed] = React.useState(false)

  return (
    <Router>
      <Layout style={{ minHeight: '100vh' }}>
        <Sidebar collapsed={collapsed} onCollapse={setCollapsed} />
        <Layout>
          <Header />
          <Content style={{ margin: '24px 16px 0', overflow: 'initial' }}>
            <div
              style={{
                padding: 24,
                backgroundColor: '#ffffff',
                minHeight: 'calc(100vh - 120px)',
              }}
            >
              <Routes>
                <Route path="/" element={<Navigate to="/dashboard" replace />} />
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/patient/:id" element={<PatientView />} />
                <Route path="/interventions" element={<InterventionPlanner />} />
                <Route path="/simulations" element={<Simulations />} />
                <Route path="/settings" element={<Settings />} />
              </Routes>
            </div>
          </Content>
        </Layout>
      </Layout>
    </Router>
  )
}

export default App
