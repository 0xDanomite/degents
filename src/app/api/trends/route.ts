// src/app/api/trends/route.ts
import { NextResponse } from 'next/server';
import { TrendService } from '@/lib/services/trendService';

const trendService = new TrendService();

export async function GET() {
  try {
    // Fetch trends from the TrendService
    const trends = await trendService.getTrends();

    // Return the trends in the response with additional metadata
    return NextResponse.json({
      trends,
      timestamp: new Date().toISOString(),
      success: true,
    });
  } catch (error) {
    // Log the error for debugging purposes
    console.error('API Error:', error);

    // Return a more detailed error response
    return NextResponse.json(
      {
        error:
          error instanceof Error
            ? error.message
            : 'Failed to fetch trends',
        success: false,
        timestamp: new Date().toISOString(),
      },
      { status: 500 }
    );
  }
}
