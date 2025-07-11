# Tierlist-User-Analysis

Do analysis on users using LA

## TODO:

- stop dupes inside main scrape
- make retrypool for timeouted pages if it becomes a problem (curr: ~1%)
- be annoyed that some users make duplicate lists that link to different endpoints but are identical, so there are dupes even though all links in main page scraping are sanitized...
- Fix server logging (add annotations, so i can see *specifically* which process has "finished")
- fix race where py node proc terminates before server internally shuts down
- rename parser file to be more descriptive

- make persistant data into database
  - Reformat dataload funcs to accomedate the change
  - if vectordb, add function for querrying when building
  - maybe do both sql and vector, so i can do sim querry, while having org data

- Functions for linear algrbra analysis
  - link on how to do clustering https://www.youtube.com/watch?v=oMtDyOn2TCc&t=542s
  - fix whatever the FUCK is wrong with the filtering
    - Infer the values maybe
    - FIX THE FUKCING NANS
    - make the axis' on the heatmap be not numbers, or ignore them entirely
- Make into CLI
