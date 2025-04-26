// src/constants/featured.ts
export interface FeaturedPlace {
  id: string;
  label: string;
}

export const featuredPlaces: FeaturedPlace[] = [
  { id: "PAR", label: "Paris, France" },
  { id: "KYO", label: "Kyoto, Japan" },
  { id: "BALI", label: "Bali, Indonesia" },
  { id: "SANT", label: "Santorini, Greece" },
  { id: "CPT", label: "Cape Town, South Africa" },
];