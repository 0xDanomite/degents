// src/lib/server/env.ts
export const serverEnv = {
  // Server-side only variables
  TWITTER_API_KEY: process.env.TWITTER_API_KEY!,
  TWITTER_API_SECRET: process.env.TWITTER_API_SECRET!,
  TWITTER_ACCESS_TOKEN: process.env.TWITTER_ACCESS_TOKEN!,
  TWITTER_ACCESS_SECRET: process.env.TWITTER_ACCESS_SECRET!,
  CDP_API_KEY: process.env.CDP_API_KEY!,
  PYTH_ENDPOINT: process.env.PYTH_ENDPOINT!,
  BASE_RPC_URL: process.env.BASE_RPC_URL!,
} as const;

// src/lib/client/env.ts
export const clientEnv = {
  // Client-side safe variables
  BASE_NETWORK: process.env.NEXT_PUBLIC_BASE_NETWORK!,
} as const;

// Validate server environment variables
Object.entries(serverEnv).forEach(([key, value]) => {
  if (!value) {
    throw new Error(`Missing server environment variable: ${key}`);
  }
});

// Validate client environment variables
Object.entries(clientEnv).forEach(([key, value]) => {
  if (!value) {
    throw new Error(`Missing client environment variable: ${key}`);
  }
});
