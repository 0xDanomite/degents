import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export const getBaseScanUrl = (
  hash: string,
  network: string = 'base-sepolia'
): string => {
  const baseUrl =
    network === 'base-mainnet'
      ? 'https://basescan.org'
      : 'https://sepolia.basescan.org';

  return `${baseUrl}/tx/${hash}`;
};
