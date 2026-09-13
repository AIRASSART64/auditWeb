import { useState } from 'react'
import html2pdf from 'html2pdf.js'

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

  // --- Exportation en JSON ---
  const telechargerJSON = () => {
    if (!resultats) return

    let hostname = 'export'
    try {
      hostname = new URL(resultats.url).hostname
    } catch {
      // Sécurité si resultats.url n'est pas une URL valide
      hostname = 'site'
    }

    const blob = new Blob([JSON.stringify(resultats, null, 2)], { type: 'application/json' })
    const href = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = href
    link.download = `audit_${hostname}_${new Date().toISOString().slice(0, 10)}.json`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(href)
  }

  // --- Exportation en PDF ---
  const telechargerPDF = () => {
    const element = document.getElementById('rapport-audit')
    if (!element) return

    const options = {
      margin: 10,
      filename: `Rapport_Audit_Web_${new Date().toISOString().slice(0, 10)}.pdf`,
      image: { type: 'jpeg', quality: 0.98 },
      html2canvas: { scale: 2 },
      jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
    }
    html2pdf().set(options).from(element).save()
  }

  // Couleur du score
  const getScoreColor = (score) => {
    if (score >= 80) return '#2e7d32' // Vert
    if (score >= 50) return '#ed6c02' // Orange
    return '#d32f2f' // Rouge
  }

  return (
    <div style={{ padding: '30px', fontFamily: "'Segoe UI', Roboto, Helvetica, Arial, sans-serif", backgroundColor: '#f8f9fa', minHeight: '100vh', color: '#333' }}>
      <header style={{ textAlign: 'center', marginBottom: '40px' }}>
        <h1 style={{ fontSize: '2.2rem', color: '#1a237e', marginBottom: '10px' }}>
          Tableau de Bord d'Audit Web
        </h1>
        <p style={{ color: '#666', fontSize: '1.1rem' }}>
          Conformité & Performance : Accessibilité (RGAA), Éco-conception (RGESN) et Vie Privée (RGPD)
        </p>
      </header>

      {/* Formulaire de saisie */}
      <div style={{ maxWidth: '800px', margin: '0 auto 40px auto', backgroundColor: '#fff', padding: '25px', borderRadius: '12px', boxShadow: '0 4px 12px rgba(0,0,0,0.08)' }}>
        <form onSubmit={lancerAudit} style={{ display: 'flex', gap: '15px' }}>
          <input
            type="url"
            placeholder="https://exemple.fr"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            required
            style={{ flex: 1, padding: '12px 16px', fontSize: '16px', border: '1px solid #ccc', borderRadius: '8px', outline: 'none' }}
          />
          <button
            type="submit"
            disabled={loading}
            style={{ padding: '12px 24px', fontSize: '16px', fontWeight: 'bold', backgroundColor: loading ? '#9e9e9e' : '#1a237e', color: '#fff', border: 'none', borderRadius: '8px', cursor: loading ? 'not-allowed' : 'pointer', transition: 'background-color 0.2s' }}
          >
            {loading ? 'Analyse en cours...' : "Lancer l'audit"}
          </button>
        </form>

        {erreur && (
          <div style={{ color: '#d32f2f', padding: '12px', border: '1px solid #ffcdd2', backgroundColor: '#ffebee', borderRadius: '8px', marginTop: '20px' }}>
            ⚠️ <strong>Erreur :</strong> {erreur}
          </div>
        )}
      </div>

      {/* Résultats d'audit */}
      {resultats && (
        <div style={{ maxWidth: '1100px', margin: '0 auto' }}>
          {/* Barres d'actions (Téléchargements) */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
            <h2 style={{ fontSize: '1.5rem', color: '#1a237e', margin: 0 }}>
              Rapport pour : <a href={resultats.url} target="_blank" rel="noreferrer" style={{ color: '#1565c0', textDecoration: 'none' }}>{resultats.url}</a>
            </h2>
            <div style={{ display: 'flex', gap: '10px' }}>
              <button
                onClick={telechargerJSON}
                style={{ padding: '10px 16px', backgroundColor: '#455a64', color: '#fff', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: '500' }}
              >
                📥 Exporter JSON
              </button>
              <button
                onClick={telechargerPDF}
                style={{ padding: '10px 16px', backgroundColor: '#2e7d32', color: '#fff', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: '500' }}
              >
                📄 Télécharger Rapport PDF
              </button>
            </div>
          </div>

          {/* Zone imprimable du Rapport */}
          <div id="rapport-audit" style={{ display: 'flex', flexDirection: 'column', gap: '25px', backgroundColor: '#f8f9fa' }}>
            
            {/* Grille des 3 Piliers */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '20px' }}>

              {/* 1. MODULE RGESN */}
              <div style={{ backgroundColor: '#fff', padding: '24px', borderRadius: '12px', boxShadow: '0 4px 12px rgba(0,0,0,0.05)', borderTop: '5px solid #2e7d32' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
                  <h3 style={{ margin: 0, color: '#2e7d32', fontSize: '1.3rem' }}>🌱 Éco-conception (RGESN)</h3>
                  <span style={{ fontSize: '1.6rem', fontWeight: 'bold', color: getScoreColor(resultats.rgesn?.score || 0) }}>
                    {resultats.rgesn?.score ?? 0}/100
                  </span>
                </div>

                <div style={{ backgroundColor: '#f1f8e9', padding: '12px', borderRadius: '8px', marginBottom: '15px' }}>
                  <p style={{ margin: '4px 0', fontSize: '0.95rem' }}>
                    <strong>Empreinte Carbone :</strong> {resultats.rgesn?.empreinte_ecologique?.co2_g_par_visite ?? 0} g CO₂ / visite
                  </p>
                  <p style={{ margin: '4px 0', fontSize: '0.95rem' }}>
                    <strong>Éco-Note :</strong> <span style={{ fontWeight: 'bold', padding: '2px 8px', borderRadius: '4px', backgroundColor: '#2e7d32', color: '#fff' }}>{resultats.rgesn?.empreinte_ecologique?.note_eco || 'N/A'}</span>
                  </p>
                </div>

                <h4 style={{ fontSize: '1rem', color: '#555', marginBottom: '8px' }}>Poids & Transfert :</h4>
                <ul style={{ paddingLeft: '20px', margin: 0, color: '#444', lineHeight: '1.6' }}>
                  <li>Poids total : <strong>{resultats.rgesn?.poids?.total_mo ?? 0} Mo</strong> ({resultats.rgesn?.poids?.total_ko ?? 0} Ko)</li>
                  <li>Nombre de requêtes HTTP : <strong>{resultats.rgesn?.reseau?.requetes_totales ?? 0}</strong></li>
                  <li>Éléments DOM : <strong>{resultats.rgesn?.dom?.elements_totaux ?? 0}</strong></li>
                </ul>

                {resultats.rgesn?.poids?.repartition_ko && (
                  <div style={{ marginTop: '15px' }}>
                    <h4 style={{ fontSize: '0.9rem', color: '#666', marginBottom: '6px' }}>Répartition du poids :</h4>
                    <div style={{ fontSize: '0.85rem', color: '#555', display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                      {Object.entries(resultats.rgesn.poids.repartition_ko).map(([type, val]) => (
                        <span key={type} style={{ backgroundColor: '#eee', padding: '3px 8px', borderRadius: '4px' }}>
                          {type}: {val} Ko
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* 2. MODULE RGAA */}
              <div style={{ backgroundColor: '#fff', padding: '24px', borderRadius: '12px', boxShadow: '0 4px 12px rgba(0,0,0,0.05)', borderTop: '5px solid #1976d2' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
                  <h3 style={{ margin: 0, color: '#1976d2', fontSize: '1.3rem' }}>♿ Accessibilité (RGAA)</h3>
                  <span style={{ fontSize: '1.6rem', fontWeight: 'bold', color: getScoreColor(resultats.rgaa?.score || 0) }}>
                    {resultats.rgaa?.score ?? 0}/100
                  </span>
                </div>

                <div style={{ display: 'flex', gap: '10px', marginBottom: '15px' }}>
                  <div style={{ flex: 1, textAlign: 'center', backgroundColor: '#ffebee', padding: '8px', borderRadius: '6px' }}>
                    <div style={{ fontSize: '1.2rem', fontWeight: 'bold', color: '#c62828' }}>{resultats.rgaa?.synthese?.critique ?? 0}</div>
                    <div style={{ fontSize: '0.75rem', color: '#c62828' }}>Critiques</div>
                  </div>
                  <div style={{ flex: 1, textAlign: 'center', backgroundColor: '#fff3e0', padding: '8px', borderRadius: '6px' }}>
                    <div style={{ fontSize: '1.2rem', fontWeight: 'bold', color: '#ef6c00' }}>{resultats.rgaa?.synthese?.grave ?? 0}</div>
                    <div style={{ fontSize: '0.75rem', color: '#ef6c00' }}>Graves</div>
                  </div>
                  <div style={{ flex: 1, textAlign: 'center', backgroundColor: '#fffde7', padding: '8px', borderRadius: '6px' }}>
                    <div style={{ fontSize: '1.2rem', fontWeight: 'bold', color: '#f57f17' }}>{resultats.rgaa?.synthese?.moyen ?? 0}</div>
                    <div style={{ fontSize: '0.75rem', color: '#f57f17' }}>Moyens</div>
                  </div>
                </div>

                <ul style={{ paddingLeft: '20px', margin: 0, color: '#444', lineHeight: '1.6' }}>
                  <li>Images sans attribut `alt` : <strong style={{ color: (resultats.rgaa?.images?.sans_alt || 0) > 0 ? '#d32f2f' : '#2e7d32' }}>{resultats.rgaa?.images?.sans_alt ?? 0}</strong> / {resultats.rgaa?.images?.total ?? 0}</li>
                  <li>Balise H1 présente : <strong>{resultats.rgaa?.structure?.presence_h1 ? 'Oui ✅' : 'Non ❌'}</strong></li>
                  <li>Total titres structurés : <strong>{resultats.rgaa?.structure?.nombre_titres ?? 0}</strong></li>
                </ul>
              </div>

              {/* 3. MODULE RGPD */}
              <div style={{ backgroundColor: '#fff', padding: '24px', borderRadius: '12px', boxShadow: '0 4px 12px rgba(0,0,0,0.05)', borderTop: '5px solid #7b1fa2' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
                  <h3 style={{ margin: 0, color: '#7b1fa2', fontSize: '1.3rem' }}>🔒 Vie Privée (RGPD)</h3>
                  {/* Correction apportée ci-dessous : ajout du `:` entre color et getScoreColor */}
                  <span style={{ fontSize: '1.6rem', fontWeight: 'bold', color: getScoreColor(resultats.rgpd?.score || 0) }}>
                    {resultats.rgpd?.score ?? 0}/100
                  </span>
                </div>

                <div style={{ backgroundColor: '#f3e5f5', padding: '12px', borderRadius: '8px', marginBottom: '15px' }}>
                  <p style={{ margin: '4px 0', fontSize: '0.95rem' }}>
                    <strong>Gestionnaire de Consentement (CMP) :</strong> {resultats.rgpd?.banniere_consentement?.nom_cmp || 'Non détecté'}
                  </p>
                </div>

                <ul style={{ paddingLeft: '20px', margin: 0, color: '#444', lineHeight: '1.6' }}>
                  <li>Traqueurs détectés : <strong>{resultats.rgpd?.traqueurs?.total_detectes ?? 0}</strong></li>
                  <li>Cookies non sécurisés : <strong>{resultats.rgpd?.cookies?.non_securises ?? 0}</strong> / {resultats.rgpd?.cookies?.total ?? 0}</li>
                  <li>Domaines tiers appelés : <strong>{resultats.rgpd?.traqueurs?.domaines_tiers_appeles?.length || 0}</strong></li>
                </ul>
              </div>

            </div>

            {/* DÉTAILS AVANCÉS : TABLEAU DES VIOLATIONS ET RECOMMANDATIONS */}
            <div style={{ backgroundColor: '#fff', padding: '24px', borderRadius: '12px', boxShadow: '0 4px 12px rgba(0,0,0,0.05)' }}>
              <h3 style={{ color: '#1a237e', marginTop: 0 }}>🔍 Violations d'Accessibilité Détaillées</h3>
              {resultats.rgaa?.violations_detaillees && resultats.rgaa.violations_detaillees.length > 0 ? (
                <div style={{ overflowX: 'auto' }}>
                  <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '10px', textAlign: 'left' }}>
                    <thead>
                      <tr style={{ backgroundColor: '#f5f5f5', borderBottom: '2px solid #ddd' }}>
                        <th style={{ padding: '10px' }}>Règle / ID</th>
                        <th style={{ padding: '10px' }}>Impact</th>
                        <th style={{ padding: '10px' }}>Description</th>
                        <th style={{ padding: '10px' }}>Éléments impactés</th>
                      </tr>
                    </thead>
                    <tbody>
                      {resultats.rgaa.violations_detaillees.map((v, idx) => (
                        <tr key={idx} style={{ borderBottom: '1px solid #eee' }}>
                          <td style={{ padding: '10px', fontFamily: 'monospace', fontWeight: 'bold' }}>{v.id}</td>
                          <td style={{ padding: '10px' }}>
                            <span style={{
                              padding: '4px 8px',
                              borderRadius: '4px',
                              fontSize: '0.8rem',
                              fontWeight: 'bold',
                              backgroundColor: v.impact === 'critical' ? '#ffebee' : v.impact === 'serious' ? '#fff3e0' : '#e8f5e9',
                              color: v.impact === 'critical' ? '#c62828' : v.impact === 'serious' ? '#ef6c00' : '#2e7d32'
                            }}>
                              {v.impact || 'moyen'}
                            </span>
                          </td>
                          <td style={{ padding: '10px' }}>{v.description}</td>
                          <td style={{ padding: '10px', textAlign: 'center', fontWeight: 'bold' }}>{v.elements_touches}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <p style={{ color: '#2e7d32' }}>✅ Aucune violation majeure détectée lors de l'analyse automatique.</p>
              )}
            </div>

          </div>
        </div>
      )}
    </div>
  )
}

export default App