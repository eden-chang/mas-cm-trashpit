/**
 * TTF → WOFF2 변환 (코펍돋움 웹 폰트 품질 개선)
 * WOFF2 사용 시 Windows/브라우저에서 안티앨리어싱·볼드 렌더링이 더 깨끗함.
 * 실행: npm run fonts:woff2
 */
import { readFile, writeFile, readdir } from 'node:fs/promises';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import ttf2woff2 from 'ttf2woff2';

const __dirname = dirname(fileURLToPath(import.meta.url));
const fontsDir = join(__dirname, '..', 'fonts');

const files = await readdir(fontsDir);
const ttfFiles = files.filter((f) => f.endsWith('.ttf'));

for (const ttf of ttfFiles) {
  const inputPath = join(fontsDir, ttf);
  const outputPath = join(fontsDir, ttf.replace(/\.ttf$/i, '.woff2'));
  const input = await readFile(inputPath);
  await writeFile(outputPath, ttf2woff2(input));
  console.log(`✓ ${ttf} → ${ttf.replace(/\.ttf$/i, '.woff2')}`);
}
