// src/app/api/agent/[action]/route.ts
import { NextResponse } from 'next/server';

const BACKEND_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

export async function POST(
  request: Request,
  { params }: { params: { action: string } }
) {
  try {
    const action = params.action;
    let body = {};

    if (action === 'auto-trading') {
      body = await request.json();
    }

    const response = await fetch(
      `${BACKEND_URL}/api/agent/${action}`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(body),
      }
    );

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error(`API Error (${params.action}):`, error);
    return NextResponse.json(
      { error: `Failed to ${params.action} agent` },
      { status: 500 }
    );
  }
}
