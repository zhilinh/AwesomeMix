$(document).ready(function(){
    let elem = document.querySelector('.slider');
    let options = {indicators: true, height: 200, interval: 6000000};
    let instance = M.Slider.init(elem, options);
    instance.pause();
});