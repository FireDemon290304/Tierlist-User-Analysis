"use strict";

import fetch from 'node-fetch';
import fs from 'fs';
import puppeteer from 'puppeteer';
import path from 'path';

// get url from py
const url = process.argv[2] || "https://tiermaker.com/list/hollow-knight/hollow-knight-areas-51862/2245367";

// get output file from py. if nor exist, set here.
const cwd = process.cwd();

// set in parent folder of this file
const outFile = process.argv[3] || path.join(cwd, 'fetchResult.json');

console.log("js loading...");

(async () => {
    const browser = await puppeteer.launch({headless:true});
    const page = await browser.newPage();

    await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36');
    await page.setExtraHTTPHeaders({
    'Accept-Language': 'en-US,en;q=0.9',
    });

    console.log("loading page", url);
    await page.goto(url, {waitUntil: 'domcontentloaded'});

    // log entire html
    //const html = await page.content();
    //fs.writeFileSync('pageContent.html', html);

    console.log("waiting for tier container");
    await page.waitForSelector('#tier-container', { timeout: 15000 }); // 15s timeout

    // make log work
    page.on('console', msg => {
        console.log("PAGE LOG:", msg.text());
    });

    console.log("tier container found, evaluating page");
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
            title,
            rows: rowObjs
        };
    });

    console.log("got:", retObj);
    fs.writeFileSync(outFile, JSON.stringify(retObj, null, 2));
    console.log("wrote to file", outFile);

    await browser.close();
})();


console.log("js done loading");
