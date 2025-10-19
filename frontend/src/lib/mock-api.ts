/**
 * Mock API utilities for simulating network delays
 */

export const mockDelay = (min = 500, max = 2000) =>
  new Promise((resolve) =>
    setTimeout(resolve, Math.random() * (max - min) + min)
  );

export async function mockFetch<T>(data: T, delayMs?: number): Promise<T> {
  if (delayMs !== undefined) {
    await new Promise((resolve) => setTimeout(resolve, delayMs));
  } else {
    await mockDelay();
  }
  return data;
}
