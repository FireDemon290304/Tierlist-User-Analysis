"use strict";

import fs from 'fs';
//import { log } from './server.js';
// dont use log, the page console will log to the serve, who will log to the file

export async function tierSub(page, singleUrl, outFile, verbose) {
    if (verbose) {
        console.log("sub mode, fetching tier list from", singleUrl);
        console.log("loading page", singleUrl);
    }
    await page.goto(singleUrl, { waitUntil: 'domcontentloaded' });

    if (verbose) console.log("waiting for tier container");
    try {
        await page.waitForSelector('#tier-container', { timeout: 15000 }); // 15s timeout
    }
    catch (error) {
        console.error("Tier container not found, page may not be a valid tier list:", error);
        return { error: "Timeout" };
    }

    if (verbose) console.log("tier container found, evaluating page");
    const retObj = await page.evaluate(() => {
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
            return { error: "Tier container not found" };
        }

        // get all rows
        const rows = Array.from(container.querySelectorAll('.tier-row'));
        console.log("found rows", rows.length);

        // Each tierrow has a div for name, then another div containing the list of ".character"s in usersorted order. just get the id for now.
        const rowObjs = rows.map(row => {
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

    if (verbose) {console.log("got:", retObj);}
    return retObj;
}

// get list of user submissions
export async function tierMain(page, url, outFile, verbose) {
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
        // get the category page
        const categoryPage = document.querySelector('#category-page');
        if (!categoryPage) {
            console.error("Category page not found");
            return { error: "Category page not found" };
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
