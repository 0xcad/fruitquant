# todo

## general
* messages css
* for the footer, stick it in a base element with min height 100% and a flex grow 1 element or smtg

## report/daily
* restyle the side nav bar / toc -- instead of position absolute, I think I can still use grid or css flex box. just to make sure that everything is centered though, have another aside of equal width, visibility 0, on the other side. use media queries to reorganize/show-hide as necessary
    * probably just restyle this in `base.html` and use another `{% block %}` to do left/right nav bars...
* smooth scroll on `#href` links + leave space for navbar

* ideally -- right works as a toc, highlighting current active link user is on and scrolling with them.
* sort on low/high price?
* add a way to collapse sections? html tag?

## commodities
* stock chart with low/high opening prices
* add option to view stock chart that's either a weekly, monthly, yearly range...
* css grid on paginated table
* can i make a way to combine json files for ytd into one? that would be huge, modify `get_report`...

right sidebar: list of vendors (on top), then a list of all fruits. don't worry about it being scrollable or whatever
if no fruit is provided it's just the list of all fruits on the right sidebar, maybe an h1 with a p underneath saying smtg like "select a fruit"


main thing that's left:
* stock chart
* css grid on pagination
* combine json files
* footer at bottom of page?
* fix `aside` with css grid, likely, or some flexbox
* some basic media queries
* links to reports with commidty href on historical prices
* automatically skip weekends, since there's no fruit reports those days. in reports the previous day should also be the previous *weekday*

* should "low price" and "high price" on commodity be median low and median high?
