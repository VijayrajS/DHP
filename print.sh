# Usage: print.sh last_page_no_of_results cutoff_date
# Date in yyyy-mm-dd
python PrintWebScraper.py $1 > results_print.csv
python PrintPageScraper.py $2
