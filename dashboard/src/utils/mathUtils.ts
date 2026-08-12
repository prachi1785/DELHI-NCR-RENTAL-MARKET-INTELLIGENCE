import type { PropertyListing } from '../types';

// Calculate median of a number array
export function getMedian(arr: number[]): number {
  if (arr.length === 0) return 0;
  const sorted = [...arr].sort((a, b) => a - b);
  const mid = Math.floor(sorted.length / 2);
  return sorted.length % 2 !== 0 ? sorted[mid] : (sorted[mid - 1] + sorted[mid]) / 2;
}

// Calculate mean of a number array
export function getMean(arr: number[]): number {
  if (arr.length === 0) return 0;
  const sum = arr.reduce((acc, val) => acc + val, 0);
  return sum / arr.length;
}

// Calculate standard deviation of a number array
export function getStdDev(arr: number[]): number {
  if (arr.length <= 1) return 0;
  const mean = getMean(arr);
  const variance = arr.reduce((acc, val) => acc + Math.pow(val - mean, 2), 0) / (arr.length - 1);
  return Math.sqrt(variance);
}

// Format Indian Currency
export function formatCurrency(num: number): string {
  if (num === undefined || num === null) return '₹0';
  return '₹' + Math.round(num).toLocaleString('en-IN');
}

// Format Compact Indian Currency (e.g. 1.2L for 120,000, 15k for 15,000)
export function formatCompactCurrency(num: number): string {
  if (num === undefined || num === null) return '₹0';
  if (num >= 100000) {
    return `₹${(num / 100000).toFixed(1)}L`;
  }
  if (num >= 1000) {
    return `₹${(num / 1000).toFixed(0)}k`;
  }
  return `₹${num}`;
}

// Format Distance
export function formatDistance(distance: number): string {
  if (distance === undefined || distance === null) return 'N/A';
  if (distance < 1) {
    return `${Math.round(distance * 1000)}m`;
  }
  return `${distance.toFixed(1)} km`;
}

// Calculate premium percentage: (yesGroupMedian - noGroupMedian) / noGroupMedian * 100
export function getPremiumPct(df: PropertyListing[], feature: keyof PropertyListing): number {
  const yesGroup = df.filter(item => item[feature] === 'Yes').map(item => item.monthly_rent);
  const noGroup = df.filter(item => item[feature] === 'No').map(item => item.monthly_rent);
  
  if (yesGroup.length === 0 || noGroup.length === 0) return 0;
  
  const yesMedian = getMedian(yesGroup);
  const noMedian = getMedian(noGroup);
  
  if (noMedian === 0) return 0;
  return ((yesMedian - noMedian) / noMedian) * 100;
}
