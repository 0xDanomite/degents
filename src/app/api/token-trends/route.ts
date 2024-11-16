import { NextResponse } from 'next/server';

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

export async function GET() {
  try {
    console.log('Fetching from:', `${API_BASE_URL}/api/token-trends`); // Debug log
    const response = await fetch(`${API_BASE_URL}/api/token-trends`);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error fetching token trends:', error);
    return NextResponse.json(
      { error: 'Failed to fetch token trends' },
      { status: 500 }
    );
  }
}
