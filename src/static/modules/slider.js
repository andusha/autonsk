class ImageSlider {
    current = -1;

    constructor(slideClass, bubbleClass) {
        this.slideClass = slideClass;
        this.bubbleClass = bubbleClass;
    }

    bubbleStyle() {
        const bubbles = document.querySelectorAll(`.${this.bubbleClass}`);
        
        for (let i = 0; bubbles.length > i; i++) {
            bubbles[i].classList.remove("bubble_active");
        }
        
        bubbles[this.current].classList.add("bubble_active");
    }
      
    slideTo(integer) {
        const slidesList = document.querySelectorAll(`.${this.slideClass}`);
        slidesList[this.current].classList.toggle("invisible");
        if (slidesList.length - 1 < this.current + integer) this.current = -1;
        else if (this.current + integer < 0) this.current = 3;
        this.current += integer;
        slidesList[this.current].classList.toggle("invisible");
        this.bubbleStyle(this.current);
    }

    timeoutSlide() {
        if (this.current >= 0) {
            const slidesList = document.querySelectorAll(`.${this.slideClass}`);
            slidesList[this.current].classList.toggle("invisible");
            if (slidesList.length - 1 < this.current + 1) this.current = -1;
            this.current += 1;
            slidesList[this.current].classList.toggle("invisible");
            this.bubbleStyle(this.current)
        } else this.current = 0;
        setTimeout(() => slider.timeoutSlide(), 5000)
    }
    
    currentSlide(integer) {
        const slidesList = document.querySelectorAll(`.${this.slideClass}`);
        
        slidesList[this.current].classList.toggle("invisible");
        slidesList[integer].classList.toggle("invisible");
        
        this.current = integer;
        
        this.bubbleStyle(this.current);
    }

    addEventToClicableObj() {
        const bubbles = document.querySelectorAll(`.${this.bubbleClass}`);
        const prev = document.querySelector('.prev');
        const next = document.querySelector('.next');

        bubbles.forEach((bubble, index) => {
            bubble.addEventListener('click', () => {
                this.currentSlide(index)
            })
        })

        prev.addEventListener('click', () => {
            this.slideTo(-1)
        })

        next.addEventListener('click', () => {
            this.slideTo(1)
        })
    }
}

