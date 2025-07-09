'use strict';

import http from 'http';
import puppeteer from 'puppeteer';
import pLimit from 'p-limit';
import fs from 'fs';
import { tierSub, tierMain } from './fetch.js';
import { Mutex } from 'async-mutex';
/*import path from 'path';
import { fileURLToPath } from 'url';*/


const PORT = 3000;
const LOG_FILE = 'server.log';
const mutex = new Mutex();
const MAX_CONCURRENT_REQUESTS = 6; // Limit concurrent requests to 10
const MAX_PAGES = 10;

/*const getPaths = (metaUrl) => {
    const __filename = fileURLToPath(import.meta.url);
    const __dirname = path.dirname(__filename);
    const parentDir = path.dirname(__dirname);
    const dataDir = path.join(parentDir, 'data');
    return { __filename, __dirname, parentDir, dataDir };
}*/

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
        await page.setExtraHTTPHeaders({'Accept-Language': 'en-US,en;q=0.9'});
        if (this.verbose) page.on('console', msg => {const url = page.url() || 'about:blank'; log(`PAGE ${url} LOG: ${msg.text()}`);});
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

async function writeFileAtomic(filePath, resObj) {
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

const server = http.createServer((req, res) => {
    log(`${req.method} ${req.url}`);
    if (req.method === 'POST') {
        if (req.url === '/scrape') {
            let body = '';
            req.on('data', chunk => body += chunk.toString());
            req.on('end', async () => {
                try {
                    // Parse the JSON body
                    const { url, outFile, isMain, verbose } = JSON.parse(body);
                    //const { __filename, __dirname, parentDir, dataDir } = getPaths(import.meta.url);

                    // Validate inputs
                    if (!url || !outFile) {
                        res.writeHead(400, { 'Content-Type': 'application/json' });
                        return res.end(JSON.stringify({ error: 'Missing required fields: url and outFile' }));
                    }

                    if (verbose) log(isMain ? "Running in MAIN mode" : "Running in SUB mode");

                    // Initialize Puppeteer
                    const browser = await puppeteer.launch({ headless: true });
                    const pagePool = new PagePool(browser, MAX_PAGES, verbose);
                    await pagePool.init();

                    const limit = pLimit(MAX_CONCURRENT_REQUESTS); // Limit concurrent requests to x

                    if (isMain) {
                        // Scrape the mainpage
                        const page = await pagePool.borrow();

                        try {
                            // writes to file insise for now
                            await tierMain(page, url, outFile, verbose);
                        }
                        finally { pagePool.release(page); }
                    } else {
                        fs.writeFileSync(outFile, ''); // empty the file to avoid appending to old data
                        // Scrape the subpage(s)
                        if (Array.isArray(url)) {
                            // promise all the pages
                            //const errors = [];
                            let numErr = 0;
                            /*const results = */
                            await Promise.all(url.map(singleUrl =>
                                limit(async () => {
                                    //todo need a way to red log in the promise
                                    if (verbose) log(`Fetching tier list from ${singleUrl}`);
                                    const page = await pagePool.borrow();

                                    try {
                                        const result = await tierSub(page, singleUrl, verbose);
                                        await writeFileAtomic(outFile, result);
                                        if (verbose) log(`Successfully processed ${singleUrl}`);
                                    }
                                    catch (error) {
                                        const errObj = { url: singleUrl, error: error.message };
                                        log(`Error processing ${singleUrl}: ${error.message}`);
                                        await writeFileAtomic(outFile, errObj);
                                        //todo make numErr += 1; work
                                        // If you want to collect errors, uncomment the following lines
                                        //fs.appendFileSync(outFile, `Error processing ${singleUrl}: ${error.message}\n`);
                                        //errors.push({ url: singleUrl, error: error.message });
                                        //return { url: singleUrl, error: error.message };
                                    }
                                    finally {
                                        if (verbose) log("Finished processing", singleUrl);
                                        pagePool.release(page);
                                    }
                                })
                            ));


                            /*if (errors.length > 0) {
                                console.error("Errors occurred during scraping:", errors);
                                log(`Errors occurred during scraping: ${errors.toString()}`);
                                res.writeHead(207, { 'Content-Type': 'application/json' });
                                return res.end(JSON.stringify({ message: 'Some URLs failed to scrape', errors }));
                            }*/
                            if (numErr > 0) {
                                log(`Errors occurred during scraping: ${numErr} URLs failed to scrape`);
                                res.writeHead(207, { 'Content-Type': 'application/json' });
                                return res.end(JSON.stringify({ message: 'Some URLs failed to scrape', errors: numErr }));
                            }
                        } else {
                            // single url
                            if (verbose) log(`Fetching tier list from ${url}`);
                            const page = await pagePool.borrow();
                            try {
                                await tierSub(page, url, verbose);
                            }
                            finally {
                                pagePool.release(page);
                            }
                        }

                        pagePool.destroy();
                        browser.close();
                    }
                    res.writeHead(200, { 'Content-Type': 'application/json' });
                    res.end(JSON.stringify({ message: 'Scraping completed successfully' }));
                } catch (error) {
                    console.error('Error during scraping:', error);
                    log(`Error during scraping: ${error.message}`);
                    res.writeHead(500, { 'Content-Type': 'application/json' });
                    res.end(JSON.stringify({ error: error.message }));
                } finally {
                    log('Request processing completed');
                }
            });
        } else if (req.url === '/stop') {
            // stop
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ message: 'Stopping server' }));
            // Close the server
            server.close(() => {
                log('Server stopped');
            });

            //todo understand why this runs, even afer the server stops?
            setTimeout(() => {
                log('Server close timeout, forcing shutdown');
                process.exit(0);
            }, 5000);
        }
    }
});

/*async function getNewPage(browser, verbose = false) {
    const page = await browser.newPage();
    await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36');
    await page.setExtraHTTPHeaders({'Accept-Language': 'en-US,en;q=0.9'});
    if (verbose) page.on('console', msg => {const url = page.url() || 'about:blank'; log(`PAGE ${url} LOG: ${msg.text()}`);});
    return page;
}*/

server.listen(PORT, () => {
  log(`Server running on http://localhost:${PORT}`);
});
