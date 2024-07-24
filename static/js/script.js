const marquee = document.querySelector('marquee');

marquee.addEventListener("mouseenter", () => {marquee.stop();})
marquee.addEventListener("mouseleave", () => {marquee.start();})
