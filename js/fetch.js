"use strict";

import { log, writeFileAtomic } from './server.js';
import { Page } from 'puppeteer';

const MAX_RETRIES = 3;
const TIMEOUT = 25000;

/**
 * Scrapes a sinlge user submission page.
 * @param { Page } page
 * @param { String } singleUrl
 * @param { boolean } verbose
 * @returns An object containing the username, the title of the submission, and a rowobject.
 *          The rowobject of the tierlist contains the name of the tier, and a list of entries. 
 */
export async function tierSub(page, singleUrl, verbose) {
    if (verbose) {
        log("sub mode, fetching tier list from", singleUrl);
        log("loading page", singleUrl);
    }
    await page.goto(singleUrl, { waitUntil: 'domcontentloaded' });

    if (verbose) log("waiting for tier container");
    try {
        await page.waitForSelector('#tier-container', { timeout: TIMEOUT }); // 25s timeout
        // made timeout lopnger to account for slow loading pages (since some tier lists have a lot of images)
    }
    catch (error) {
        console.error("Tier container not found, page may not be a valid tier list:", error);
        log(`ERROR: Tier container not found after ${TIMEOUT} ms: ${error}`)
        return { error: "Timeout" };
    }

    if (verbose) log("tier container found, evaluating page");
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
        const userName = userElement ? userElement.textContent.replace('Follow @', '').trim().replace('>', '') : 'Unknown User';

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

    if (verbose) { log(`got: ${retObj} from ${singleUrl}`); }
    return retObj;
}


/**
 * Scrape the main pages for links to user sumbissions
 * @param { Page } page 
 * @param { String } url 
 * @param { String } outFile 
 * @param { boolean } verbose 
 * @returns null
 */
export async function tierMain(page, url, outFile, verbose) {
    /**
     ** Will contain id="category-page": div for list
     ** class="list-item lazy": div for each item in list
        ** get the anchor tag inside to get the link (sans base url)
     */

    let currPage = 1;
    let baseUrl = new URL(url);
    //log("base url:", baseUrl.toString());

    baseUrl.searchParams.set('page', currPage);
    baseUrl.searchParams.set('sort', 'recent');

    if (verbose) log("First base url: " + baseUrl.toString());

    let pageUrl = baseUrl.toString();

    //let promises = [];
    let users = new Set(); // avoid dupes

    /**
     * element to look for:
     * <a class="pagination" href="?page=186&amp;sort=">last page</a>
     */

    // find total number of pages by clicking the "last page" button
    if (verbose) log("Getting total number of pages");
    await page.goto(pageUrl, { waitUntil: 'domcontentloaded' });
    try {
        await page.waitForSelector('#pagination a.pagination', { timeout: TIMEOUT });
    } catch (error) {
        console.error("Pagination not found, page may not be a valid category list:", error);
        log(`ERROR: Pagination not found: ${error}`);
        return { error: "Timeout" };
    }
    const numPages = await page.evaluate(() => {
        // find the last page link
        const paginationLinks = document.querySelectorAll('#pagination a.pagination');
        const lastPageLink = Array.from(paginationLinks).find(a => a.textContent.toLowerCase().trim() === 'last page');
        if (lastPageLink) {
            // inside the link, get the href attribute
            const lastPageUrl = lastPageLink.getAttribute('href');
            // get the searchparam: page
            const url = new URL(lastPageUrl, document.baseURI);
            return url.searchParams.get('page');
        } else {
            console.error("Last page link not found");
            return null;   // todo thow error here?
        }
    });
    if (verbose) log("Total number of pages was:" + numPages);

    let numRetries = 0;
    while (currPage <= numPages) {
        try {
            if (numRetries <= MAX_RETRIES) {
                await page.goto(pageUrl, { waitUntil: 'domcontentloaded' });
            } else { currPage++; continue; }
        }
        catch {
            log(`Failed to go to ${pageUrl}: Retry number ${numRetries++}`);
            continue;
        }
        // find the category page
        try {
            await page.waitForSelector('#category-page', { timeout: 15000 }); // 15s timeout
        } catch (error) {
            console.error("Failed to find page", pageUrl, "error:", error);
            if (currPage === 1) {
                console.error("No items found on the first page, exiting.");
                log("No items found on the first page, exiting.");
                break;
            }
            else {
                console.error("No more items found, exiting.");
                break; // no more pages
            }
        }

        // get curr page urls
        if (verbose) log("Category page found: Getting page urls for page " + currPage);
        const pageUrlsObjs = await getPageUrls(page);

        pageUrlsObjs.forEach(async element => {
            if (element && !users.has(element)) {
                users.add(element);
                await writeFileAtomic(outFile, element);
            }
        });

        currPage++;
        baseUrl.searchParams.set('page', currPage);
        pageUrl = baseUrl.toString();

        await new Promise(resolve => setTimeout(resolve, 500)); // wait 500ms before next request
    }
}

/**
 * Get the urls for users on this page index of the main page.
 * @param { Page } page 
 * @returns Object containing a list of links
 */
async function getPageUrls(page) {
    return await page.evaluate(() => {
        // get the category page
        const categoryPage = document.querySelector('#category-page');
        if (!categoryPage) {
            console.error("Category page not found");
            return { error: "Category page not found" };
        }

        // get all items in the list
        const items = Array.from(categoryPage.querySelectorAll('.list-item.lazy'));
        console.log("Found items", items.length);

        // map each item to its link
        const links = items.map(item => {
            const anchor = item.querySelector('a');
            return anchor ? anchor.getAttribute('href') : null;
        }).filter(link => link !== null); // filter out nulls

        return links;
    });
}
