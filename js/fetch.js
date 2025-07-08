"use strict";

import fs from 'fs';
//import { log } from './server.js';
// dont use log, the page console will log to the serve, who will log to the file

export async function tierSub(page, singleUrl, verbose) {
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

    let currPage = 1;
    let baseUrl = new URL(url);
    console.log("base url:", baseUrl.toString());

    baseUrl.searchParams.set('page', currPage);
    baseUrl.searchParams.set('sort', 'recent');

    if (verbose) console.log("first base url:", baseUrl.toString());

    let pageUrl = baseUrl.toString();

    //let promises = [];
    let users = new Set(); // avoid dupes

    /**
     * element to look for:
     * <a class="pagination" href="?page=186&amp;sort=">last page</a>
     */

    // find total number of pages by clicking the "last page" button
    if (verbose) console.log("getting total number of pages");
    await page.goto(pageUrl, { waitUntil: 'domcontentloaded' });
    try {
        await page.waitForSelector('#pagination a.pagination', { timeout: 15000 }); // 15s timeout
    } catch (error) {
        console.error("Pagination not found, page may not be a valid category list:", error);
        return { error: "Timeout" };
    }
    const numPages = await page.evaluate(() => {
        // find the last page link
        const paginationLinks = document.querySelectorAll('#pagination a.pagination');
        const lastPageLink = Array.from(paginationLinks).find(a => a.textContent.trim().toLowerCase() === 'last page');
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
    if (verbose) console.log("total number of pages:", numPages);

    while (currPage <= numPages) {
        await page.goto(pageUrl, { waitUntil: 'domcontentloaded' });
        // find the category page
        if (verbose) console.log("waiting for category page");
        try {
            await page.waitForSelector('#category-page', { timeout: 15000 }); // 15s timeout
        } catch (error) {
            console.error("failed to find page", pageUrl, "error:", error);
            if (currPage === 1) {
                console.error("No items found on the first page, exiting.");
                break;
            }
            else {
                console.error("No more items found, exiting.");
                break; // no more pages
            }
        }

        // get curr page urls
        if (verbose) console.log("category page found: getting page urls for page " + currPage + ". Adding to set");
        const pageUrlsObjs = await getPageUrls(page);

        // insert into set
        pageUrlsObjs.forEach(url => {
            if (url) {
                users.add(url);
            }
        });

        // do this later with a page obj pool
        /*// add page as promise
        promises.push(getPageUrls(page))
            .then(urls => {
                retObj[currPage] = pageUrlsObjs;
            })
            .catch(error => {
                console.error(`Error fetching page ${currPage}:`, error);
                retObj[currPage] = { error: error.message };
            });*/

        // check if there are more pages "pagination" class + "next page >" text inside anchor tag
        if (verbose) console.log("checking for next page button");

        /*const hasNextPage = await page.evaluate(() => {
            const paginationLinks = document.querySelectorAll('#pagination a.pagination');
            console.log("found pagination links:", paginationLinks.length);
            const texts = Array.from(paginationLinks).map(a => a.textContent.trim());
            return texts.some(text => text.toLowerCase().includes('next page'));
        });
        if (!hasNextPage) {
            if (verbose) console.log("no more pages found, exiting" + (currPage > 1 ? " after page " + currPage : ""));
            break; // no more pages
        }*/

        currPage++;
        baseUrl.searchParams.set('page', currPage);
        pageUrl = baseUrl.toString();

        await new Promise(resolve => setTimeout(resolve, 1000));
    }

    const retObj = JSON.stringify([...users], null, 2); // convert set to array and stringify

    if (verbose) console.log("got:", retObj);
    fs.writeFileSync(outFile, retObj);
    if (verbose) console.log("wrote to file", outFile);
}

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
        console.log("found items", items.length);

        // map each item to its link
        const links = items.map(item => {
            const anchor = item.querySelector('a');
            return anchor ? anchor.getAttribute('href') : null;
        }).filter(link => link !== null); // filter out nulls

        return links;
    });
}
