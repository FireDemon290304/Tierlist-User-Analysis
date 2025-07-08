# Tierlist-User-Analysis

Do analysis on users using LA

## TODO:

- stop dupes inside main scrape
- make progress updates to log outside verbose for sub pages
- make retrypool for timeouted pages if it becomes a problem (curr: ~1%)
- if jsonl file gets too large before i go to db, simply make fewer letters/do abbr
- be annoyed that some users make duplicate lists that link to different endpoints but are identical, so there are dupes even though all links in main page scraping are sanitized...
- make check when instancing node server, so i dont have to comment out stuff during debug in VSCode
- Fix server logging (add annotations, so i can see *specifically* which process has "finished")
- fix race where py node proc terminates before server internally shuts down
- rename parser file to be more descriptive
- make persistant data into database
  - Reformat dataload funcs to accomedate the change
  - if vectordb, add function for querrying when building
  - maybe do both sql and vector, so i can do sim querry, while having org data
- Functions for linear algrbra analysis
- Make into CLI
