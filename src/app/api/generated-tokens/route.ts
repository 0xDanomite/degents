import { NextResponse } from 'next/server';

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

export async function GET() {
  try {
    const response = await fetch(
      `${API_BASE_URL}/api/generated-tokens`
    );

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error fetching generated tokens:', error);
    return NextResponse.json(
      { error: 'Failed to fetch generated tokens' },
      { status: 500 }
    );
  }
}
