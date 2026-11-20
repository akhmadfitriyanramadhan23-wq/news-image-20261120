// news-image-20261120 — one image summing up Friday 20 November 2026.
// The picture itself lives beside this file as entry.png, drawn by
// tools/make-image.py from that day's verified news, and this program's
// only job is to hand that exact file to the grader as /output/entry.png.
// Nothing is generated or fetched at run time, so two runs always write
// the same bytes. The program first makes sure the output directory
// exists, so it works in a fresh directory as well as a reused one, and
// it prints the path and size it wrote for the run log.
//
// Outside the grader's container, MAKEFUN_OUTPUT_DIR stands in for /output:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, existsSync, mkdirSync, statSync } from 'node:fs';
import { join } from 'node:path';

const outputDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
if (!existsSync(outputDir)) mkdirSync(outputDir, { recursive: true });
const outputPath = join(outputDir, 'entry.png');
copyFileSync(new URL('./entry.png', import.meta.url), outputPath);
console.log(`wrote ${outputPath} (${statSync(outputPath).size} bytes)`);
