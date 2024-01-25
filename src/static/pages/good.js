function priceSlider() {
    const tableFilter = new TableUI(slider)
    const rangeInput = document.querySelectorAll(".range-input input"),
    priceInput = document.querySelectorAll(".price-input input"),
    range = document.querySelector(".slider .progress");
    let priceGap = 1;
    priceInput.forEach((input) => {
    input.addEventListener("input", (e) => {
        let minPrice = parseInt(priceInput[0].value),
        maxPrice = parseInt(priceInput[1].value);

        if (maxPrice - minPrice >= priceGap && maxPrice <= rangeInput[1].max) {
        if (e.target.className === "input-min") {
            rangeInput[0].value = minPrice;
        } else {
            rangeInput[1].value = maxPrice;
        }
        console.log('2')
        tableFilter.tableFilter(minPrice, maxPrice)
        }
    });
    });

    rangeInput.forEach((input) => {
    input.addEventListener("input", (e) => {
        let minVal = parseInt(rangeInput[0].value),
        maxVal = parseInt(rangeInput[1].value);

        if (maxVal - minVal < priceGap) {
        if (e.target.className === "range-min") {
            rangeInput[0].value = maxVal - priceGap;
        } else {
            rangeInput[1].value = minVal + priceGap;
        }
        } else {
        priceInput[0].value = minVal;
        priceInput[1].value = maxVal;
        }
    });
    });
};

class Filter {
    sortedList;

    constructor(dataList) {
        this.dataList = dataList
    }
    
    orderBy(order, sortMethod) {
        const orderByDict = {'info': 0, 'price': 1, 'amount': 2, 'period': 3}
        this.sortedList = _.orderBy(this.dataList, (p) => p[orderByDict[order]], sortMethod)

        return this.sortedList
    }

    sliderSort(min, max){
        function inBetween(value, min, max){
            return value >= min && value <= max;
        }     
        this.sortedList = _.filter(this.dataList, (p) => inBetween(p[1], min, max))

        return this.sortedList
    }
}

class TableUI{
    sortedList;

    constructor(elem){
        elem.onclick = this.updateTable.bind(this);
        this.elem = elem
        this.flag = this.elem.dataset.flag
        this.filter = new Filter(data)
        this.thead = thead
        this.tbody = tbody
    }

    tableSort() {
        let th = event.target.closest('th');
        if (!th.classList.contains('th-sortable')) return;

        const thList = this.thead.querySelectorAll('.th-sortable')
        for (const i of thList) {
            if (th!=i) i.dataset.sortMethod = 'none'
        }

        const arrowsList = this.thead.querySelectorAll('.thead-arrows')
        const arrows = th.querySelector('.thead-arrows')
        for (const arrow of arrowsList) {
            if (arrow!=arrows){
            arrow.classList = []
            arrow.classList.add('thead-arrows')
            }
        }
        let type = th.dataset.type;
        switch (th.dataset.sortMethod){
            case 'none':
                th.dataset.sortMethod = 'asc'
                arrows.classList.add('thead-arrows__asc')
                break
            case 'asc':
                th.dataset.sortMethod = 'desc'
                arrows.classList.remove('thead-arrows__asc')
                arrows.classList.add('thead-arrows__desc')
                break
            case 'desc':
                arrows.classList.remove('thead-arrows__desc')
                th.dataset.sortMethod = 'none'
                break
        }

        this.sortedList = this.filter.orderBy(type,th.dataset.sortMethod)
        this.tbody.innerHTML = this.tableCreateRow(this.sortedList)
    }

    tableCreateRow(sortedList){
        const manufacturerTitle = document.querySelector('.product-titles').dataset.manufacturerTitle
        const productId = document.querySelector('.product-titles').dataset.productId
        const productTitle = document.querySelector('.product-titles').dataset.productTitle
        let tbodyRows = `
                <tr class="title-row">
                    <td colspan=8>
                        <div class="title-container">
                            <div class="title-section">Запрошенный номер</div>
                            <div class="total-section">${sortedList.length}</div>
                        </div>
                    </td>
                </tr>`

        for (let data of sortedList) {
            let imgHtml = ''
            switch (data[0]) {
                case 1:
                    imgHtml = `<img src="${data[4]}" title="Надёжный поставщик">`
                    break
                case 2:
                    imgHtml = `<img src="${data[4]}" title="Дилер">`
                    break
            }
            let row = `
                        <tr>
                            <td><div class="table-manufacturer-title">${manufacturerTitle}</div></td>
                            <td><div class="table-good-number">${productId}</div></td>
                            <td>
                                <div class="table-good-info">
                                    ${imgHtml}
                                </div>
                            </td>
                            <td><div class="table-good-title">${productTitle}</div></td>
                            <td><div class="table-good-amount">${data[2]}</div></td>
                            <td><div class="table-good-period">${data[3]}</div></td>
                            <td><div class="table-good-price">${data[1]}</div></td>
                            <td><button>))</button></td>
                        </tr> `
            tbodyRows += row  
        }

        return tbodyRows
    }

    tableFilter(minPrice = 0, maxPrice = 0) {
        let filteredList
        if (minPrice){
            filteredList = this.filter.sliderSort(minPrice, maxPrice)
            this.tbody.innerHTML = this.tableCreateRow(filteredList)
            return filteredList
        }
        const priceInputs = document.querySelectorAll('.field')
        let min = priceInputs[0].firstChild.value
        let max = priceInputs[1].firstChild.value
        filteredList = this.filter.sliderSort(min, max)
        this.tbody.innerHTML = this.tableCreateRow(filteredList)
        return filteredList
    }
    updateTable(event){
        console.log(this.flag)
        switch (this.flag){
            case 'false':
                this.tableSort()
                break
            case 'true':
                this.tableFilter()
                break
        }
    }

}

const tableSort = new TableUI(thead)
priceSlider()