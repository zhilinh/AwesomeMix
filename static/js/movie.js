$(document).ready(function(){
    let elem = document.querySelector('.slider');
    let options = { indicators: true, height: 200 };
    let instance = M.Slider.init(elem, options);
    instance.pause();
});