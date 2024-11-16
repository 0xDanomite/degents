// src/app/api/trends/route.ts
import { NextResponse } from 'next/server';
import { TrendService } from '@/lib/services/trendService';

const trendService = new TrendService();

export async function GET() {
  try {
    const trends = await trendService.getTrends();

    return NextResponse.json({
      trends,
      timestamp: new Date().toISOString(),
      success: true,
    });
  } catch (error) {
    console.error('API Error:', error);

    return NextResponse.json(
      {
        error: 'Failed to fetch trends',
        success: false,
        timestamp: new Date().toISOString(),
      },
      { status: 500 }
    );
  }
}
