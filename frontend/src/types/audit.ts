export interface ViolationDetail {
  id: string;
  impact: 'minor' | 'moderate' | 'serious' | 'critical';
  description: string;
  elements_touches: number;
}

export interface RGAAData {
  score: number;
  resume_gravite: {
    critique: number;
    grave: number;
    moyen: number;
    mineur: number;
  };
  violations_detaillees: ViolationDetail[];
}

export interface RGPDData {
  score: number;
  banniere_consentement: {
    detectee: boolean;
    nom_cmp: string;
  };
  cookies: {
    total: number;
    non_securises: number;
  };
  traqueurs: {
    total_detectes: number;
    liste: string[];
  };
}

export interface RGESNData {
  score: number;
  empreinte_ecologique: {
    co2_g_par_visite: number;
    energie_kwh_par_visite: number;
    note_eco: 'A' | 'B' | 'C' | 'D' | 'E';
  };
  poids: {
    total_mo: number;
    repartition_ko: Record<string, number>;
  };
}

export interface AuditResponse {
  url: string;
  rgaa: RGAAData;
  rgpd: RGPDData;
  rgesn: RGESNData;
}