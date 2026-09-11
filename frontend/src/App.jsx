import { useEffect, useState } from 'react'

function App() {
  const [message, setMessage] = useState('Connexion au backend...')

  useEffect(() => {
    fetch('http://127.0.0.1:8000/')
      .then((res) => res.json())
      .then((data) => setMessage(data.message))
      .catch(() => setMessage('Erreur : impossible de contacter le backend '))
  }, [])

  return (
    <div style={{ padding: '40px', fontFamily: 'sans-serif' }}>
      <h1>AuditFlow</h1>
      <p>Statut du Backend : <strong>{message}</strong></p>
    </div>
  )
}

export default App