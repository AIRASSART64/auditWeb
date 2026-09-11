import { useState } from 'react'

function App() {
  const [url, setUrl] = useState('')
  const [resultats, setResultats] = useState(null)
  const [loading, setLoading] = useState(false)
  const [erreur, setErreur] = useState('')

  const lancerAudit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setErreur('')
    setResultats(null)

    try {
      const response = await fetch(`http://127.0.0.1:8000/api/audit/?url=${encodeURIComponent(url)}`)
      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || "Erreur lors de l'analyse")
      }

      setResultats(data)
    } catch (err) {
      setErreur(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ padding: '40px', fontFamily: 'sans-serif', maxWidth: '800px', margin: '0 auto' }}>
      <h1> Conformité RGPD RGAA et RGESN</h1>

      <form onSubmit={lancerAudit} style={{ marginBottom: '30px' }}>
        <input
          type="url"
          placeholder="https://exemple.fr"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          required
          style={{ width: '70%', padding: '10px', fontSize: '16px', marginRight: '10px' }}
        />
        <button type="submit" disabled={loading} style={{ padding: '10px 20px', fontSize: '16px' }}>
          {loading ? 'Analyse...' : 'Lancer l audit'}
        </button>
      </form>

      {erreur && (
        <div style={{ color: 'red', padding: '10px', border: '1px solid red', borderRadius: '4px' }}>
          {erreur}
        </div>
      )}

      {resultats && (
        <div>
          <h2>Résultats pour {resultats.url}</h2>
          <div style={{ display: 'flex', gap: '20px', marginTop: '20px' }}>

            {/* RGESN */}
            <div style={{ border: '1px solid #ddd', padding: '15px', borderRadius: '8px', flex: 1 }}>
              <h3>RGESN (Éco-conception)</h3>
              <p style={{ fontSize: '24px', fontWeight: 'bold' }}>{resultats.rgesn.score} / 100</p>
              <p>Poids HTML : {resultats.rgesn.poids_ko} Ko</p>
            </div>

            {/* RGAA */}
            <div style={{ border: '1px solid #ddd', padding: '15px', borderRadius: '8px', flex: 1 }}>
              <h3>RGAA (Accessibilité)</h3>
              <p style={{ fontSize: '24px', fontWeight: 'bold' }}>{resultats.rgaa.score} / 100</p>
              <p>Images sans alt : {resultats.rgaa.images_sans_alt} / {resultats.rgaa.total_images}</p>
            </div>

            {/* RGPD */}
            <div style={{ border: '1px solid #ddd', padding: '15px', borderRadius: '8px', flex: 1 }}>
              <h3>RGPD </h3>
              <span>Données personnelles</span>
              <p style={{ fontSize: '24px', fontWeight: 'bold' }}>{resultats.rgpd.score} / 100</p>
              <p>Traqueurs : {resultats.rgpd.trackers_detectes}</p>
            </div>

          </div>
        </div>
      )}
    </div>
  )
}

export default App