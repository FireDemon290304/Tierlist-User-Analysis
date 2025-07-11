'use strict';

import http from 'http';
import puppeteer from 'puppeteer';
import pLimit from 'p-limit';
import fs, { read } from 'fs';
import { tierSub, tierMain } from './fetch.js';
import { Mutex } from 'async-mutex';
import readline from 'readline';
/*import path from 'path';
import { fileURLToPath } from 'url';*/


const PORT = 3000;
const LOG_FILE = 'server.log';
const MAX_CONCURRENT_REQUESTS = 6; // Limit concurrent requests to 10
const MAX_PAGES = 10;
const mutex = new Mutex();

class PagePool {
    constructor(browser, size, verbose) {
        this.browser = browser;
        this.size = size;
        this.verbose = verbose;
        this.pool = [];
        this.queue = [];
    }

    async init() {
        for (let i = 0; i < this.size; i++) {
            const page = await this.createPage();
            this.pool.push(page);
        }
    }

    async createPage() {
        const page = await this.browser.newPage();
        await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36');
        await page.setExtraHTTPHeaders({ 'Accept-Language': 'en-US,en;q=0.9' });
        if (this.verbose) {
            page.on('console', msg => {
                const url = page.url() || 'about:blank';
                const urlObj = new URL(url);

                // Extract path segments
                const pathParts = urlObj.pathname.split('/');
                const catNameId = pathParts[pathParts.length - 1];

                // Extract page number from query parameters
                const pageNumber = urlObj.searchParams.get('page') || '-1';

                // Enhanced log format with consistent spacing and structure
                log(`[${new Date().toISOString()}] PAGE ${catNameId}-p${pageNumber} LOG: ${msg.text()}`);
            });
        }
        return page;
    }


    async borrow() {
        if (this.pool.length > 0) {
            return this.pool.pop();
        }
        return new Promise((resolve) => {
            this.queue.push(resolve);
        });
    }

    // todo update to destroy bad pages and replace them
    async release(page) {
        if (this.queue.length > 0) {
            const resolve = this.queue.shift();
            resolve(page);
        } else { this.pool.push(page); }
    }

    async destroy() {
        for (const page of this.pool) {
            await page.close();
        }
        this.pool = [];
        this.queue = [];
    }
}

export async function writeFileAtomic(filePath, resObj) {
    await mutex.runExclusive(() => {
        fs.writeFileSync(filePath, JSON.stringify(resObj) + '\n', { flag: 'a' });
    });
}

export function log(message) {
    const timestamp = new Date().toISOString();
    const logMessage = `[${timestamp}] ${message}\n`;
    // Log to console AND append to file
    console.log(message);
    fs.appendFileSync(LOG_FILE, logMessage);
}

const server = http.createServer(async (req, res) => {
    log(`${req.method} ${req.url}`);

    if (req.method === 'POST') {
        if (req.url === '/scrape') {
            // Headers are automatically lowercased by node (apparently)
            const isMain = req.headers['x-is-main'] === 'true';
            const outFile = req.headers['x-outfile'];
            const verbose = req.headers['x-verbose'] === 'true';

            if (!outFile) {
                res.writeHead(400, { 'Content-Type': 'application/json' });
                return res.end(JSON.stringify({ error: 'X-Outfile header is required' }));
            }

            // Handle request errors (e.g., client disconnects)
            req.on('error', (err) => {
                log(`REQUEST STREAM ERROR: ${err.message}`);
            });

            log(`Verbose set to ${verbose}`);

            // ===============================================
            //  MAIN MODE: Scrape a single page for its links
            // ===============================================
            if (isMain) {
                log("Running in MAIN mode.");
                let body = '';
                req.on('data', chunk => body += chunk.toString());
                req.on('end', async () => {
                    const url = body.trim();

                    // Initialize Puppeteer
                    const browser = await puppeteer.launch({ headless: true });
                    const page = await browser.newPage();
                    await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36');
                    await page.setExtraHTTPHeaders({ 'Accept-Language': 'en-US,en;q=0.9' });
                    if (verbose) page.on('console', msg => { const url = page.url() || 'about:blank'; log(`PAGE ${url} LOG: ${msg.text()}`); });

                    try {
                        fs.writeFileSync(outFile, ''); // Clear old file
                        await tierMain(page, url, outFile, verbose);
                        res.writeHead(200, { 'Content-Type': 'application/json' });
                        res.end(JSON.stringify({ message: `Main page scraped. Links saved to ${outFile}` }));
                    } catch (error) {
                        log(`ERROR in MAIN mode: ${error.message}`);
                        res.writeHead(500, { 'Content-Type': 'application/json' });
                        res.end(JSON.stringify({ error: error.message }));
                    } finally {
                        await browser.close();
                        log('Main mode finished. Browser closed.');
                    }
                });
            }
            // ====================================================
            //  SUB MODE: Scrape a stream of URLs from the request
            // ====================================================
            else {
                log("Running in SUB mode. Initializing browser and page pool...");
                const browser = await puppeteer.launch({ headless: true });
                const pagePool = new PagePool(browser, MAX_PAGES, verbose); // Assuming PagePool is defined
                await pagePool.init();

                const limit = pLimit(MAX_CONCURRENT_REQUESTS);
                const promises = [];
                fs.writeFileSync(outFile, ''); // Clear old file

                const rl = readline.createInterface({ input: req });

                rl.on('line', (url) => {
                    if (url) {
                        const promise = limit(async () => {
                            const page = await pagePool.borrow();
                            if (verbose) log(`Processing: ${url}`);
                            try {
                                const result = await tierSub(page, url, verbose);
                                await writeFileAtomic(outFile, result);
                            } catch (error) {
                                log(`ERROR processing ${url}: ${error.message}`);
                                await writeFileAtomic(outFile, { url, error: error.message });
                            } finally {
                                pagePool.release(page);
                            }
                        });
                        promises.push(promise);
                    }
                });

                rl.on('close', async () => {
                    log('Finished reading URL stream. Waiting for all scrapes to complete...');
                    try {
                        await Promise.all(promises);
                        log('All scraping tasks finished successfully.');
                        res.writeHead(200, { 'Content-Type': 'application/json' });
                        res.end(JSON.stringify({ message: 'Scraping completed' }));
                    } catch (error) {
                        log(`ERROR waiting for promises: ${error.message}`);
                        res.writeHead(500, { 'Content-Type': 'application/json' });
                        res.end(JSON.stringify({ error: 'One or more scraping tasks failed.' }));
                    } finally {
                        await pagePool.destroy();
                        await browser.close();
                        log('Sub mode finished. Browser closed.');
                    }
                });
            }
        } else if (req.url === '/stop') {
            const TO = 5000;
            log('Received stop request.');
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ message: 'Stopping server' }));
            // Close the server
            server.close(() => {
                log('Server stopped');
                process.exit(0);
            });

            setTimeout(() => {
                log(`Internal error: Server close timeout ${TO} reached, forcing shutdown`);
                process.exit(0);
            }, TO);
        }
        else {
            res.writeHead(404, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ message: 'Not Found' }));
        }
    }
});

server.listen(PORT, () => {
    log(`Server running on http://localhost:${PORT}`);
});
