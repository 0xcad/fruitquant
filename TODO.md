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
* footer to be always on bottom of page (need some flex grow column stuff in main content)
* fix `aside` with css grid, likely, or some flexbox
* some basic media queries
* automatically skip weekends, since there's no fruit reports those days. in reports the previous day should also be the previous *weekday*

* should "low price" and "high price" on commodity be median low and median high?

re media queries:
* ideally, the page layout is the main column with all the content, and then the aside
* when the page gets too small, the aside should fold in to be *below* the navbar, but above the rest of the page content
* *if* i didn't have to worry about the navbar this would be easy. i would just have the nav, the wrapper for the main col + aside, and then use `flex flow: row wrap` and `flex-direction: reverse` when the time called for it
* however, for position sticky to work on the nav i think it needs to be in the main column div

idea:
* could i place the aside panel in the main column, then use position absolute to drag it out to the side. i just use media queries to set it to be non-position absolute to "fold it" back in. this is it, yeah, that's the plan
