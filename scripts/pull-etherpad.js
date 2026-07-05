#!/usr/bin/env node
/**
 * Pulls rendered HTML from an Etherpad pad and writes it into
 * content/notion-content.json, in the same shape index.html already expects:
 *   { content: "<...html...>", lastUpdated: "ISO-8601 string" }
 *
 * Required env vars:
 *   ETHERPAD_URL      e.g. https://uescan-website.fly.dev
 *   ETHERPAD_API_KEY  from /data/APIKEY.txt on the Etherpad instance
 *   PAD_ID            (optional) defaults to "uescan-homepage"
 */

const fs = require('fs');
const path = require('path');

const ETHERPAD_URL = process.env.ETHERPAD_URL;
const ETHERPAD_API_KEY = process.env.ETHERPAD_API_KEY;
const PAD_ID = process.env.PAD_ID || 'uescan-homepage';
const OUTPUT_PATH = path.join(__dirname, '..', 'content', 'notion-content.json');

if (!ETHERPAD_URL || !ETHERPAD_API_KEY) {
  console.error('Missing ETHERPAD_URL or ETHERPAD_API_KEY environment variables.');
  process.exit(1);
}

async function fetchPadHTML(padId) {
  const url = `${ETHERPAD_URL}/api/1/getHTML?padID=${encodeURIComponent(padId)}&apikey=${ETHERPAD_API_KEY}`;
  const res = await fetch(url);
  const data = await res.json();

  if (data.code !== 0) {
    throw new Error(`Etherpad API error for pad "${padId}": ${data.message || 'unknown error'}`);
  }
  return data.data.html;
}

// Etherpad's getHTML returns a full <html><head>...</head><body>...</body></html>
// document. index.html supplies its own page chrome and just injects this into
// a <div class="notion-content">, so we only want the inner body content.
function extractBodyContent(rawHtml) {
  const match = rawHtml.match(/<body[^>]*>([\s\S]*)<\/body>/i);
  return match ? match[1].trim() : rawHtml.trim();
}

// Etherpad has no native "blockquote" button. Convention: any line an editor
// starts with "> " (in the pad) gets wrapped in <blockquote> so it picks up
// your existing .notion-content blockquote styling. Consecutive "> " lines
// are merged into a single blockquote.
function convertBlockquoteConvention(html) {
  const lines = html.split(/(?=<p>|<div>)/i);
  let inQuote = false;
  const out = [];

  for (const line of lines) {
    const isQuoteLine = /^<(p|div)[^>]*>\s*&gt;\s?/i.test(line);
    const stripped = line.replace(/^<(p|div)[^>]*>\s*&gt;\s?/i, '<p>').trim();

    if (isQuoteLine && !inQuote) {
      out.push('<blockquote>' + stripped);
      inQuote = true;
    } else if (isQuoteLine && inQuote) {
      out.push(stripped);
    } else if (!isQuoteLine && inQuote) {
      out[out.length - 1] += '</blockquote>';
      inQuote = false;
      out.push(line);
    } else {
      out.push(line);
    }
  }
  if (inQuote) out[out.length - 1] += '</blockquote>';

  return out.join('');
}

async function main() {
  console.log(`Fetching pad "${PAD_ID}" from ${ETHERPAD_URL}...`);
  const rawHtml = await fetchPadHTML(PAD_ID);
  let bodyContent = extractBodyContent(rawHtml);
  bodyContent = convertBlockquoteConvention(bodyContent);

  const output = {
    content: bodyContent,
    lastUpdated: new Date().toISOString(),
  };

  fs.mkdirSync(path.dirname(OUTPUT_PATH), { recursive: true });
  fs.writeFileSync(OUTPUT_PATH, JSON.stringify(output, null, 2));

  console.log(`Wrote ${OUTPUT_PATH}`);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
