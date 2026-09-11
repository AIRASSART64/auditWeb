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
      // 1. Mise à jour de l'URL et passage en POST
      const response = await fetch(
        `http://127.0.0.1:8000/api/audit/analyser?url=${encodeURIComponent(url)}`,
        { method: 'POST' }
      )
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
    <div style={{ padding: '40px', fontFamily: 'sans-serif', maxWidth: '900px', margin: '0 auto' }}>
      <h1>Conformité RGPD, RGAA et RGESN</h1>

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
          {loading ? 'Analyse en cours...' : "Lancer l'audit"}
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
              <p style={{ fontSize: '24px', fontWeight: 'bold', color: '#2e7d32' }}>
                {resultats.rgesn.score} / 100
              </p>
              <p>Poids : <strong>{resultats.rgesn.poids.total_mo} Mo</strong></p>
              <p>CO₂ : <strong>{resultats.rgesn.empreinte_ecologique.co2_g_par_visite} g</strong> / visite</p>
              <p>Note : <strong>{resultats.rgesn.empreinte_ecologique.note_eco}</strong></p>
            </div>

            {/* RGAA */}
            <div style={{ border: '1px solid #ddd', padding: '15px', borderRadius: '8px', flex: 1 }}>
              <h3>RGAA (Accessibilité)</h3>
              <p style={{ fontSize: '24px', fontWeight: 'bold', color: '#1976d2' }}>
                {resultats.rgaa.score} / 100
              </p>
              <p>Erreurs critiques : <strong>{resultats.rgaa.synthese.critique}</strong></p>
              <p>Images sans alt : <strong>{resultats.rgaa.images.sans_alt}</strong> / {resultats.rgaa.images.total}</p>
            </div>

            {/* RGPD */}
            <div style={{ border: '1px solid #ddd', padding: '15px', borderRadius: '8px', flex: 1 }}>
              <h3>RGPD (Vie Privée)</h3>
              <p style={{ fontSize: '24px', fontWeight: 'bold', color: '#7b1fa2' }}>
                {resultats.rgpd.score} / 100
              </p>
              <p>Traqueurs : <strong>{resultats.rgpd.traqueurs.total_detectes}</strong></p>
              <p>CMP : <strong>{resultats.rgpd.banniere_consentement.nom_cmp}</strong></p>
            </div>

          </div>
        </div>
      )}
    </div>
  )
}

export default App