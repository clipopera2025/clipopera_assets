const axios = require('axios');
const cheerio = require('cheerio');
const { HttpsProxyAgent } = require('https-proxy-agent');

/**
 * Discover prompt-related pages from a category archive.
 * Defaults to the "Free Prompt Sets" archive on sprinkleofai.com.
 * Usage: node scripts/discover_prompt_pages.js [archiveUrl]
 */
async function discoverPromptPages(archiveUrl = 'https://sprinkleofai.com/free-prompt-sets/') {
  const keywords = ['prompt', 'prompts', 'midjourney'];
  const proxy = process.env.HTTPS_PROXY || process.env.https_proxy || null;
  const agent = proxy ? new HttpsProxyAgent(proxy) : undefined;
  const { data } = await axios.get(archiveUrl, {
    headers: { 'User-Agent': 'Mozilla/5.0 (compatible; PromptScraper/1.0)' },
    httpsAgent: agent,
    proxy: false,
    maxRedirects: 5,
  });
  const $ = cheerio.load(data);
  const links = new Set();
  $('a').each((i, el) => {
    const href = $(el).attr('href');
    const text = $(el).text();
    if (!href) return;
    const lowerHref = href.toLowerCase();
    const lowerText = text.toLowerCase();
    if (keywords.some(k => lowerHref.includes(k) || lowerText.includes(k))) {
      const fullUrl = href.startsWith('http') ? href : `https://sprinkleofai.com${href}`;
      links.add(fullUrl);
    }
  });
  return Array.from(links);
}

if (require.main === module) {
  const urlArg = process.argv[2];
  discoverPromptPages(urlArg).then(res => {
    console.log('Discovered prompt pages:');
    res.forEach(link => console.log(link));
  }).catch(err => {
    console.error('Failed to fetch prompt pages:', err.message);
    process.exit(1);
  });
}

module.exports = discoverPromptPages;
