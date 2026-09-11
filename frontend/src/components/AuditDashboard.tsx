import React from 'react';
import { AuditResponse } from '../types/audit';

interface Props {
  data: AuditResponse;
}

export const AuditDashboard: React.FC<Props> = ({ data }) => {
  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold">Résultats d'audit pour : {data.url}</h1>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        
        {/* Carte RGAA */}
        <div className="p-4 border rounded-lg shadow-sm bg-white">
          <h2 className="text-xl font-semibold mb-2">Accessibilité (RGAA)</h2>
          <div className="text-4xl font-bold text-blue-600 mb-4">{data.rgaa.score} / 100</div>
          <div className="text-sm space-y-1">
            <p className="text-red-600">Erreurs critiques : {data.rgaa.resume_gravite.critique}</p>
            <p className="text-orange-500">Erreurs graves : {data.rgaa.resume_gravite.grave}</p>
          </div>
        </div>

        {/* Carte RGESN */}
        <div className="p-4 border rounded-lg shadow-sm bg-white">
          <h2 className="text-xl font-semibold mb-2">Éco-conception (RGESN)</h2>
          <div className="flex items-center space-x-3 mb-4">
            <span className="text-4xl font-bold text-green-600">{data.rgesn.score} / 100</span>
            <span className="px-3 py-1 bg-green-100 text-green-800 font-bold rounded-full">
              Note {data.rgesn.empreinte_ecologique.note_eco}
            </span>
          </div>
          <p className="text-sm">CO₂ / visite : <strong>{data.rgesn.empreinte_ecologique.co2_g_par_visite} g</strong></p>
          <p className="text-sm">Poids total : <strong>{data.rgesn.poids.total_mo} Mo</strong></p>
        </div>

        {/* Carte RGPD */}
        <div className="p-4 border rounded-lg shadow-sm bg-white">
          <h2 className="text-xl font-semibold mb-2">Vie Privée (RGPD)</h2>
          <div className="text-4xl font-bold text-purple-600 mb-4">{data.rgpd.score} / 100</div>
          <p className="text-sm">
            CMP : {data.rgpd.banniere_consentement.detectee 
              ? <span className="text-green-600 font-medium">{data.rgpd.banniere_consentement.nom_cmp}</span>
              : <span className="text-red-500">Non détectée</span>}
          </p>
          <p className="text-sm">Traqueurs détectés : <strong>{data.rgpd.traqueurs.total_detectes}</strong></p>
        </div>

      </div>
    </div>
  );
};