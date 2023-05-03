const categories = document.getElementById("categories");
const food = document.getElementById("food");
const preloader = document.getElementById("loading");
const search = document.querySelector('header div input');
const body = document.querySelector('body');

const CATEGORIES_URL = "https://www.themealdb.com/api/json/v1/1/categories.php";
const CATEGORY_CLICK_URL = "https://www.themealdb.com/api/json/v1/1/filter.php?c=";
const MEAL_SEARCH_URL = "https://www.themealdb.com/api/json/v1/1/lookup.php?i=";
const INGREDIANT_IMAGE_URL = "https://www.themealdb.com/images/ingredients/";
const SEARCH_URL = "https://www.themealdb.com/api/json/v1/1/search.php?s=";
const INGREDIANT_SEARCH_URL = 'https://www.themealdb.com/api/json/v1/1/filter.php?i=';

function loading() {
    preloader.style.display = "none";
    body.style.overflowY = "scroll";
}


// if(preloader.classList.contains('hidden')){

// }

// setTimeout(function () {
//     get_categories(CATEGORIES_URL);
// }, 2000);

get_categories(CATEGORIES_URL)

function get_categories(url) {
    categories.innerHTML = ``;

    fetch(url).then(res => res.json()).then(data => {
        console.log(data);

        for (let i = 0; i < data.categories.length; i++) {
            const category = document.createElement('div');
            category.classList.add('category');
            category.innerHTML = `
            <div id="${data.categories[i].idCategory}">
        <h1>${data.categories[i].strCategory}</h1>
        <img src="${data.categories[i].strCategoryThumb}">
        </div>
        `
            categories.appendChild(category);
            let id = data.categories[i].idCategory;
            document.getElementById(id).addEventListener('click', () => {
                console.log(data.categories[i].strCategory);
                let category = data.categories[i].strCategory;
                open_category(CATEGORY_CLICK_URL, category);
            })

        }

    })
}

function open_category(url, category) {
    fetch(url + category).then(res => res.json()).then(data => {
        console.log(data);
        categories.innerHTML = ``;
        food.innerHTML = ``;
        if (data.meals != 'null') {
            for (let i = 0; i < data.meals.length; i++) {
                const category = document.createElement('div');
                category.classList.add('category');
                category.innerHTML = `
            <div id="${data.meals[i].idMeal}">
        <h1>${data.meals[i].strMeal}</h1>
        <img src="${data.meals[i].strMealThumb}">
        </div>
        `
                categories.appendChild(category);
                let id = data.meals[i].idMeal;
                document.getElementById(id).addEventListener('click', () => {
                    console.log(id);
                    open_food(MEAL_SEARCH_URL, id);
                })

            }
        }
        else {
            category.innerHTML = `<h1>No Result Found</h1>`
        }
    });
}


function open_food(url, id) {
    fetch(url + id).then(res => res.json()).then(data => {
        console.log(data);

        // Filter list 

        const meal = data.meals[0];
        const ingredients = [];
        const measures = [];
        const image_url = [];

        for (let i = 1; i <= 20; i++) {
            const thisIngredient = meal[`strIngredient${i}`];
            const thisMeasure = meal[`strMeasure${i}`];
            if (thisIngredient) {
                ingredients.push(thisIngredient);
                measures.push(thisMeasure);
            }
        }

        const filteredIngredients = ingredients.filter(Boolean);
        const filteredMeasures = measures.filter(Boolean);

        console.log(filteredIngredients);
        console.log(filteredMeasures);


        categories.innerHTML = ``;
        food.innerHTML = ``;
        food.innerHTML = `
        <div class="title">
            <h1>${data.meals[0].strMeal}</h1>
        </div>
        <div class="food-container" id="food-container">
            <div class="data">
                <img src="${data.meals[0].strMealThumb}">
                <span>${data.meals[0].strArea}</span>
                <span>${data.meals[0].strCategory}</span>
            </div>
            <div class="ingredients" id="ingredients">
            </div>
        </div>

        `
        for (let i = 0; i <= filteredIngredients.length - 1; i++) {
            console.log(filteredIngredients[i]);
            const url = INGREDIANT_IMAGE_URL + filteredIngredients[i] + '.png';
            image_url.push(url);
            console.log(image_url[i]);

            const ingrediant = document.createElement('div');
            ingrediant.classList.add('ingredient');
            ingrediant.innerHTML = `
            <div id="${filteredIngredients[i]}" >
            <img src="${image_url[i]}" style="max-width: 10vw;" ">
                        <span >${filteredIngredients[i]}</span>
                        <span>${filteredMeasures[i]}</span>
                        </div>

            
                    `;

            document.getElementById("ingredients").appendChild(ingrediant);
            let id = filteredIngredients[i];
            document.getElementById(id).addEventListener('click', () => {
                console.log(id);
                open_category(INGREDIANT_SEARCH_URL, id);
            });


        }
        const instructions = document.createElement('div');
        instructions.classList.add('instructions');
        const youtube_url = data.meals[0].strYoutube;
        const videoId = youtube_url.split("=")[1];
        instructions.innerHTML = `
        <div class="instructions">
            <h1>Instructions</h1>
            <span>${data.meals[0].strInstructions}</span>
        </div>
        <div class="youtube">
            <iframe width="560" height="315" src="https://www.youtube.com/embed/${videoId}"
                title="YouTube video player" frameborder="0"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                allowfullscreen></iframe>
        </div>`;
        food.appendChild(instructions);
    })
}


// Search meal

search.addEventListener('keypress', function (e) {
    if (e.key === 'Enter') {
        e.preventDefault();
        const data = search.value;
        console.log(data);
        search_meal(SEARCH_URL, data);

    }
})


function search_meal(url, data) {
    fetch(url + data).then(res => res.json()).then(data => {
        console.log(data);
        food.innerHTML = ``;
    })
    open_category(url, data);
}
