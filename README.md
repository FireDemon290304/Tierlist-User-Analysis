# Tierlist-User-Analysis

Do analysis on users using LA

## TODO:

- scrape pages sequentially from mainpages, not just page 1, so we get more then 8 first user entries
  - if json gets too large before i go to db, simply make fewer letters/do abbr
- Fix server logging (add annotations, so i can see *specifically* which process has "finished")
- fix race where py node proc terminates before server internally shuts down
- rename parser
- make persistant data into database
  - Reformat dataload funcs to accomedate the change
  - if vectordb, add function for querrying when building
- Functions for linear algrbra analysis
- Make into CLI
