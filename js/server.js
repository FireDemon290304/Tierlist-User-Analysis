'use strict';

import http from 'http';
import puppeteer from 'puppeteer';
import pLimit from 'p-limit';
import fs from 'fs';
import { tierSub, tierMain } from './fetch.js';

const PORT = 3000;
const LOG_FILE = 'server.log';

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

                    // Validate inputs
                    if (!url || !outFile) {
                        res.writeHead(400, { 'Content-Type': 'application/json' });
                        return res.end(JSON.stringify({ error: 'Missing required fields: url and outFile' }));
                    }

                    if (verbose) log(isMain ? "Running in MAIN mode" : "Running in SUB mode");

                    // Initialize Puppeteer
                    const browser = await puppeteer.launch({ headless: true });

                    const limit = pLimit(5); // Limit concurrent requests to 5

                    if (isMain) {
                        // Scrape the mainpage
                        const page = await getNewPage(browser, verbose);

                        // writes to file insise for now
                        await tierMain(page, url, outFile, verbose);
                        await page.close();
                    } else {
                        fs.writeFileSync(outFile, ''); // empty the file to avoid appending to old data
                        // Scrape the subpage(s)
                        if (Array.isArray(url)) {
                            // promise all the pages
                            const errors = [];
                            const results = await Promise.all(url.map(singleUrl =>
                                limit(async () => {
                                    //todo need a way to red log in the promise
                                    if (verbose) log(`Fetching tier list from ${singleUrl}`);
                                    //verbose = false;
                                    const page = await getNewPage(browser, verbose);
                                    //verbose = true;
                                    try {
                                        return await tierSub(page, singleUrl, outFile, verbose);
                                    }
                                    catch (error) {
                                        console.error(`Error processing ${singleUrl}:`, error);
                                        fs.appendFileSync(outFile, `Error processing ${singleUrl}: ${error.message}\n`);
                                        errors.push({ url: singleUrl, error: error.message });
                                        return { url: singleUrl, error: error.message };
                                    }
                                    finally {
                                        if (verbose) log("Finished processing", singleUrl);
                                        await page.close();
                                    }
                                })
                            ));

                            results.forEach(result => {
                                fs.appendFileSync(outFile, JSON.stringify(result) + '\n');
                            });

                            if (errors.length > 0) {
                                console.error("Errors occurred during scraping:", errors);
                                log(`Errors occurred during scraping: ${errors.toString()}`);
                                res.writeHead(207, { 'Content-Type': 'application/json' });
                                return res.end(JSON.stringify({ message: 'Some URLs failed to scrape', errors }));
                            }
                        } else {
                            // single url
                            if (verbose) log(`Fetching tier list from ${url}`);
                            const page = await getNewPage(browser, verbose);
                            await tierSub(page, url, outFile, verbose);
                            await page.close();
                        }
                    }

                    await browser.close();

                    res.writeHead(200, { 'Content-Type': 'application/json' });
                    res.end(JSON.stringify({ message: 'Scraping completed successfully' }));
                } catch (error) {
                    console.error('Error during scraping:', error);
                    log(`Error during scraping: ${error.message}`);
                    res.writeHead(500, { 'Content-Type': 'application/json' });
                    res.end(JSON.stringify({ error: error.message }));
                }
                finally {
                    //await browser.close();
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

            setTimeout(() => {
                log('Server close timeout, forcing shutdown');
                process.exit(0);
            }, 5000);
        }
    }
});

async function getNewPage(browser, verbose = false) {
    const page = await browser.newPage();
    await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36');
    await page.setExtraHTTPHeaders({'Accept-Language': 'en-US,en;q=0.9'});
    if (verbose) page.on('console', msg => {const url = page.url() || 'about:blank'; log(`PAGE ${url} LOG: ${msg.text()}`);});
    return page;
}

server.listen(PORT, () => {
  log(`Server running on http://localhost:${PORT}`);
});
