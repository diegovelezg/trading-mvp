/**
 * AssetBadge Component
 *
 * Muestra ICONO de sector + badge de tipo de instrumento.
 * Soporta dos formatos de data:
 * 1. Explorer: {sector, asset_type}
 * 2. Watchlist: {assetType}
 */

import { Badge } from "@/components/ui/badge";
import { classifyAssetFromDB, InstrumentType } from "@/lib/asset-classifier";
import {
  Cpu, Zap, Stethoscope, Landmark, Wrench, FlaskConical,
  Building, ShoppingCart, Tag, RadioTower, Circle, DollarSign,
  Layers, Package, Factory
} from "lucide-react";
import { Tooltip, TooltipContent, TooltipTrigger, TooltipProvider } from "@/components/ui/tooltip";

interface AssetBadgeProps {
  tickerDetail?: {
    sector?: string;
    asset_type?: string;
    assetType?: string;  // Watchlist format
  };
  showInstrumentType?: boolean;
  size?: "sm" | "md" | "lg";
}

const INSTRUMENT_LABELS: Record<InstrumentType, string> = {
  stock: "Stock",
  etf: "ETF",
  adr: "ADR",
  reit: "REIT",
  unit_mlp: "Unit/MLP",
  fund: "Fund",
  other: "",
};

const INSTRUMENT_COLORS: Record<InstrumentType, string> = {
  stock: "bg-zinc-800 border-zinc-700 text-zinc-400",
  etf: "bg-blue-950/50 border-blue-800 text-blue-400",
  adr: "bg-purple-950/50 border-purple-800 text-purple-400",
  reit: "bg-teal-950/50 border-teal-800 text-teal-400",
  unit_mlp: "bg-orange-950/50 border-orange-800 text-orange-400",
  fund: "bg-green-950/50 border-green-800 text-green-400",
  other: "",
};

/**
 * Mapea sector (string) a icono basado en palabras clave
 */
function getSectorIcon(sector: string): React.ComponentType<{ className?: string }> {
  const s = sector.toLowerCase();

  if (s.includes('energ') || s.includes('energy') || s.includes('uranio') || s.includes('oil')) {
    return Zap;
  }
  if (s.includes('tec') || s.includes('tech') || s.includes('semiconductor')) {
    return Cpu;
  }
  if (s.includes('salud') || s.includes('health') || s.includes('medic')) {
    return Stethoscope;
  }
  if (s.includes('finanzas') || s.includes('financ') || s.includes('banca') || s.includes('bank')) {
    return Landmark;
  }
  if (s.includes('industrial') || s.includes('infraestructura') || s.includes('manufactur')) {
    return Wrench;
  }
  if (s.includes('material') || s.includes('químic') || s.includes('chemical')) {
    return FlaskConical;
  }
  if (s.includes('bienes') || s.includes('real estate') || s.includes('inmueble')) {
    return Building;
  }
  if (s.includes('consum') || s.includes('retail') || s.includes('comerci')) {
    return ShoppingCart;
  }
  if (s.includes('servic') || s.includes('utility') || s.includes('eléctric')) {
    return RadioTower;
  }
  if (s.includes('ingeniería') || s.includes('engineering') || s.includes('construcción')) {
    return Factory;
  }
  if (s.includes('bond') || s.includes('bono') || s.includes('fixed income')) {
    return DollarSign;
  }

  return Circle;
}

function getSectorColor(sector: string): string {
  // Siempre gris, independientemente del sector
  return "text-zinc-400";
}

export function AssetBadge({ tickerDetail, showInstrumentType = true, size = "sm" }: AssetBadgeProps) {
  // Normalizar ambos formatos de data
  const normalizedDetail = {
    sector: tickerDetail?.sector || tickerDetail?.assetType?.split(' ').slice(-1)[0], // Fallback: usar última palabra de assetType
    asset_type: tickerDetail?.asset_type || tickerDetail?.assetType
  };

  const classification = classifyAssetFromDB(normalizedDetail);

  // Si no hay data útil, no mostrar nada
  if (!normalizedDetail.sector && classification.instrumentType === 'other') {
    return null;
  }

  const SectorIcon = normalizedDetail.sector ? getSectorIcon(normalizedDetail.sector) : Circle;
  const sectorColor = normalizedDetail.sector ? getSectorColor(normalizedDetail.sector) : "text-zinc-400";

  const sizeClasses = {
    sm: "w-3 h-3",
    md: "w-4 h-4",
    lg: "w-5 h-5",
  };

  // Si es stock (default), no mostrar badge de tipo
  const showBadge = showInstrumentType && classification.instrumentType !== "stock" && classification.instrumentType !== "other";

  return (
    <div className="flex items-center gap-2">
      {/* Icono de Sector con Tooltip */}
      {normalizedDetail.sector && (
        <TooltipProvider>
          <Tooltip>
            <TooltipTrigger>
              <div className={`flex items-center ${sectorColor}`}>
                <SectorIcon className={sizeClasses[size]} />
              </div>
            </TooltipTrigger>
            <TooltipContent side="top">
              <p className="text-xs">{normalizedDetail.sector}</p>
            </TooltipContent>
          </Tooltip>
        </TooltipProvider>
      )}

      {/* Badge de Tipo de Instrumento (solo si no es stock) */}
      {showBadge && (
        <Badge className={`text-[8px] px-1.5 py-0 border ${INSTRUMENT_COLORS[classification.instrumentType]} pointer-events-none`}>
          {INSTRUMENT_LABELS[classification.instrumentType]}
        </Badge>
      )}
    </div>
  );
}
