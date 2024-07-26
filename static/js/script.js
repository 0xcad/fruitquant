const marquee = document.querySelector('marquee');

marquee.addEventListener("mouseenter", () => {marquee.stop();})
marquee.addEventListener("mouseleave", () => {marquee.start();})


function scrollIntoView(targetEl) {
  if (!targetEl)
      return;
    var targetElPosition = targetEl.getBoundingClientRect().top;
    var targetElOffset = targetElPosition + window.pageYOffset - NAV_HEIGHT;
    window.scrollTo({
         top: targetElOffset,
         behavior: "smooth"
    });
}

const NAV_HEIGHT = 32;
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function (e) {
    e.preventDefault();

    var targetEl = document.querySelector(this.getAttribute('href'));
    scrollIntoView(targetEl);
  });
});

window.addEventListener('load', (e) => {
  console.log('hey!');
  if (window.location.hash) {
    var targetEl = document.querySelector(window.location.hash);
    scrollIntoView(targetEl);
  }
});
