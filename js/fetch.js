"use strict";

import fetch from 'node-fetch';
import fs from 'fs';
import puppeteer, { Page } from 'puppeteer';
import path from 'path';

console.log("Start js logs");

// get url from py
const url = process.argv[2];// || "https://tiermaker.com/categories/hollow-knight/hollow-knight-areas-51862";

// get output file from py. if nor exist, set here.
const cwd = process.cwd();

// set in parent folder of this file
const outFile = process.argv[3] || path.join(cwd, 'fetchResult.json');

// todo clean run flag

// get flag for main or sub
const isMain = process.argv[4] === "isMain" || process.argv[4] === "true" || process.argv[4] == "1";
const verbose = process.argv[5] === "verbose" || process.argv[5] === "true" || process.argv[5] == "1";
//const verbose = true;

if (verbose) {
    console.log("Running verbose");
} else {
    console.log("Running non verbose");
}
console.log("js loading...");

async function tierSub(page) {
    if (verbose) {
        console.log("sub mode, fetching tier list from", url);
        console.log("loading page", url);
    }
    await page.goto(url, { waitUntil: 'domcontentloaded' });

    // log entire html
    //const html = await page.content();
    //fs.writeFileSync('pageContent.html', html);

    if (verbose) {
        console.log("waiting for tier container");
    }
    await page.waitForSelector('#tier-container', { timeout: 15000 }); // 15s timeout

    if (verbose) {console.log("tier container found, evaluating page");}
    const retObj = await page.evaluate(() => {
        console.log("evaluating page");

        /*
            * Relevant info in one item:
                * - h1:title
                * - div:Class:container: Top
                    * - div:Class: tier-row: rows
                        * - div:Class: label-holder
                            * - span:Class:Label:text: name of tier 
                        * - div:Class:tier sort: container for items
                            * - div:Class:character: each item in the tier (contains id and image)
        */

        // todo get user
        // username in class="follow-button" which contains an anchor witth the name as text.
        // formatted as "Follow @username". We need to extract the username only, sans the "Follow @" part.
        // get user name
        const userElement = document.querySelector('.follow-button a');
        const userName = userElement ? userElement.textContent.replace('Follow @', '').trim() : 'Unknown User';

        // get title
        const titleElement = document.querySelector('h1');
        const title = titleElement ? titleElement.textContent.trim() : 'Untitled Tier List';

        //get container
        const container = document.querySelector('#tier-container');
        if (!container) {
            console.error("Tier container not found");
            return []; // todo error
        }

        // get all rows
        const rows = Array.from(container.querySelectorAll('.tier-row'));
        console.log("found rows", rows.length);

        // Each tierrow has a div for name, then another div containing the list of ".character"s in usersorted order. just get the id for now.
        rowObjs = rows.map(row => {
            // get label
            const labelHolder = row.querySelector('.label-holder');
            const tierName = labelHolder ? labelHolder.textContent.trim() : 'Unnamed Tier';

            // get all entries in row
            const characters = Array.from(row.querySelectorAll('.character'));
            return {
                tierName,
                entries: characters.map(char => char.id)
            };
        });

        // return end obj
        return {
            userName,
            title,
            rows: rowObjs
        };
    });

    // todo append to file rather than overwrite

    if (verbose) {console.log("got:", retObj);}
    fs.writeFileSync(outFile, JSON.stringify(retObj, null, 2));
    if (verbose) {console.log("wrote to file", outFile);}
}

// get list of user submissions
async function tierMain(page) {
    /**
     ** Will contain id="category-page": div for list
     ** class="list-item lazy": div for each item in list
        ** get the anchor tag inside to get the link (sans base url)
     */
    if (verbose) {
        console.log("main mode, fetching tier list from", url);
        console.log("loading page", url);
    }

    await page.goto(url, { waitUntil: 'domcontentloaded' });

    // find the category page
    if (verbose) console.log("waiting for category page");
    await page.waitForSelector('#category-page', { timeout: 15000 }); // 15s timeout

    if (verbose) console.log("category page found, evaluating page");
    const retObj = await page.evaluate(() => {
        console.log("evaluating page");

        // get the category page
        const categoryPage = document.querySelector('#category-page');
        if (!categoryPage) {
            console.error("Category page not found");
            return []; // todo error
        }

        // get all items in the list
        const items = Array.from(categoryPage.querySelectorAll('.list-item.lazy'));
        console.log("found items", items.length);

        // map each item to its link
        const links = items.map(item => {
            const anchor = item.querySelector('a');
            return anchor ? anchor.getAttribute('href') : null;
        }).filter(link => link !== null); // filter out nulls

        return links;
    });

    if (verbose) console.log("got:", retObj);
    fs.writeFileSync(outFile, JSON.stringify(retObj, null, 2));
    if (verbose) console.log("wrote to file", outFile);
}

async function main() {
    const browser = await puppeteer.launch({ headless: true });
    const page = await browser.newPage();

    await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36');
    await page.setExtraHTTPHeaders({
        'Accept-Language': 'en-US,en;q=0.9'
    });

    // make log work
    if (verbose) {
        console.log("Setting up page console logging");
        page.on('console', msg => {
            console.log("PAGE LOG:", msg.text());
        });
    }

    const thing = isMain ? tierMain : tierSub;

    thing(page)
        .then(() => { console.log("finished work: End js logs"); })
        .catch(err => { console.error("Error:", err); })
        .finally(() => { browser.close(); });
}

main();

console.log("js done loading");
