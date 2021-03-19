var tbody = d3.select('#recipetable');

/////////////////////////////////////////////////////////////////////////
// PROJECT 3 ADDITION ///////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////
// test
// We didn't use .then() because of the version of d3 we are using, as I understand it
//d3.json("/api/recipemetadata").then((recipes) => {
   //console.log(recipes)
//});
/////////////////////////////////////////////////////////////////////////

d3.json("/api/recipemetadata", function(recipes){
    console.log(recipes)
});


/////////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////
// FUNCTION buildTable()
/////////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////

// Create function to generate and populate the table
function buildTable() { 

    // tbody.html('');

    d3.json("/api/recipemetadata", function(recipes){
        recipes.forEach(record => {
        var row = tbody.append('tr');
            ////logic: if checked -- identify the status as checked and if not set status to unchecked; add a status true or flase to records pulled from API
            // function that counts the number of recipes and then assigns an number incrementing by 1
            x = 0
            for (var i=0, len=recipes.length; i< len; i++) {
                x = x + 1
            };           

            row.append('td').append('input').attr("type", "checkbox").attr('id', `${record['recipe_id']}`).attr('title', `${record['recipe_title']}`).attr('class', 'recipe-checkbox');
            // row.append('td').text(record['recipe_id']);
            // row.append('td').text(record['recipe_title']).attr('title', `${record['recipe_title']}`);
            row.append('td').append('a')
                .attr('href', record['source_url'])
                .attr('target', '_blank')
                .text(record['recipe_title']);
            // row.append('td').text(record['likes']);
            // row.append('td').text(record['health_score']);
            row.append('td').text(record['calories_serving']);
            // row.append('td').text(record['carbohydrates_serving']);
            row.append('td').text(record['servings']);
            row.append('td').text(record['cooking_minutes']);
            console.log(record)
            console.log("work")

        });

        /////////////////////////////////////////////////////////////////////////
        // PROJECT 3 ADDITION ///////////////////////////////////////////////////
        /////////////////////////////////////////////////////////////////////////
        // 20210312 - calling this function within the promise to ensure that 
        //              the event listener is attached before the elements is "destroyed" in the DOM
        activateTableEventListeners();
        /////////////////////////////////////////////////////////////////////////
    });
};

buildTable()

/////////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////
// FUNCTION refreshTable()
/////////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////

function refreshTable(data) {

    console.log('----- IN REFRESH TABLE ')
    console.log(data);

    tbody.html('');

    data.forEach(record => {
    var row = tbody.append('tr');
////logic: if checked -- identify the status as checked and if not set status to unchecked; add a status true or flase to records pulled from API
        row.append('td').append('input').attr("type", "checkbox").attr('id', `${record['recipe_id']}`).attr('title', `${record['recipe_title']}`).attr('class', 'recipe-checkbox');
        // row.append('td').text(record['recipe_id']);
        // row.append('td').text(record['recipe_title']).attr('title', `${record['recipe_title']}`);
        row.append('td').append('a')
            .attr('href', record['source_url'])
            .attr('target', '_blank')
            .text(record['recipe_title']);
        // row.append('td').text(record['likes']);
        // row.append('td').text(record['health_score']);
        row.append('td').text(record['calories_serving']);
        // row.append('td').text(record['carbohydrates_serving']);
        row.append('td').text(record['servings']);
        row.append('td').text(record['cooking_minutes']);
        console.log(record)
    });
    
    // clear existing tbody    
    // loop through the filtered data to populate the tbody

        /////////////////////////////////////////////////////////////////////////
        // PROJECT 3 ADDITION ///////////////////////////////////////////////////
        /////////////////////////////////////////////////////////////////////////
        // 20210312 - there is no "promise" in this function, so it is fine to call this here
        activateTableEventListeners();
        /////////////////////////////////////////////////////////////////////////

};


/////////////////////////////////////////////////////////////////////////
// PROJECT 3 ADDITION ///////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////
// FUNCTION addCheckedData()
/////////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////

// NOTE: we used this to debug our Event Listener / "promise" issue

function addCheckedData(){

    console.log("---clicked checkbox should activate this message---");

    checkedItem = d3.event.target;
    itemTitle = checkedItem['title'];
    console.log("---checkedItem---");
    console.log(itemTitle);
       
};


// /////////////////////////////////////////////////////////////////////////
// /////////////////////////////////////////////////////////////////////////
// // FUNCTION recipemetadataAPIreturn()
// /////////////////////////////////////////////////////////////////////////
// /////////////////////////////////////////////////////////////////////////

function recipemetadataAPIreturn(){
    // Create a copy of tableData specifically for filtering
   
    console.log('filter table event')

    // capture value for all search fields */
    var query = d3.select('#query').property('value');
    var cuisine = d3.select('#cuisine').property('value');
    var diet = d3.select('#diet').property('value'); 
    var type_of_recipe = d3.select('#type_of_recipe').property('value');   
    var intolerances = d3.select('#intolerances').property('value');

    var filterFields

    // Build an object of fields to run through 
    var filterFields = {
        'query': query,
        'cuisine': cuisine,
        'diet': diet,
        'type_of_recipe': type_of_recipe,
        'intolerances': intolerances
    }

    // Remove empty keys from the list of filters to search
    Object.entries(filterFields).forEach(([key, val]) => {
        
        // Use !val to check for empty strings or nulls
        if(!val) { 
            delete filterFields[key];
        }
    });

    console.log('----filterFields----')
    console.log(filterFields)

    // PASS query fields and values to Flask API/recipemetadata route and on to Spoonacular API
    // RETURNS query results from Spoonacular API via Flask Flask API/recipemetadata route
    // which POPULATES the returned data into our page 1 table using refreshTable() function

    d3.json(`/api/recipemetadata?query=${query}&cuisine=${cuisine}&diet=${diet}&type_of_recipe=${type_of_recipe}&intolerances=${intolerances}&`, function(data){
        console.log(diet);
        refreshTable(data); 
    });
    activateTableEventListeners()
}


// /////////////////////////////////////////////////////////////////////////
// /////////////////////////////////////////////////////////////////////////
// // FUNCTION formReset()
// /////////////////////////////////////////////////////////////////////////
// /////////////////////////////////////////////////////////////////////////

// // Clear out input fields in the Filter Form, wipe the Table, and rebuild the Table with pristine original data
function formReset() {
    document.getElementById("filter-form").reset(); 
    tbody.html('');
    buildTable();
};



// /////////////////////////////////////////////////////////////////////////
// // PROJECT 3 ADDITION ///////////////////////////////////////////////////
// /////////////////////////////////////////////////////////////////////////
// /////////////////////////////////////////////////////////////////////////
// /////////////////////////////////////////////////////////////////////////
// // FUNCTION addRecipeWeekplan()
// /////////////////////////////////////////////////////////////////////////
// /////////////////////////////////////////////////////////////////////////

function addRecipeWeekplan() {
    
    // output the value of the dayofweek dropdown that was selected
    // if statement or switch/case to indicate which col to select based on day of week

    var dayOfWeek = d3.select('#dayofweek').node().value;
    console.log(dayOfWeek);
    var elem = '';
    console.log(dayOfWeek);

    switch(dayOfWeek) {
        case 'Sunday':
            elem = '#td-sunday'
            console.log(elem);
            break;
        case 'Monday':
            elem = '#td-monday'
            console.log(elem);
            break;
        case 'Tuesday':
            elem = '#td-tuesday'
            console.log(elem);
            break;
        case 'Wednesday':
            elem = '#td-wednesday'
            console.log(elem);
            break;
        case 'Thursday':
            elem = '#td-thursday'
            console.log(elem);
            break;
        case 'Friday':
            elem = '#td-friday'
            console.log(elem);
            break;
        case 'Saturday':
            elem = '#td-saturday'
            console.log(elem);
            break;
    };
    
    td = d3.select(elem);
    
    checkeddataX = d3.selectAll('input.recipe-checkbox:checked');
    console.log("---checkeddataX---");
    console.log(checkeddataX);
    
    checkeddataX.each(function() {
        // title = d3.select(this).attr('recipe_title');        
        // console.log("---title---")
        // console.log(title)
        td.append('p').text(this.title).attr("id", this.id);
    });

};

// /////////////////////////////////////////////////////////////////////////
// /////////////////////////////////////////////////////////////////////////
// // EVENT LISTENERS
// /////////////////////////////////////////////////////////////////////////
// /////////////////////////////////////////////////////////////////////////

// // Call the function to initially load the table
// buildTable();

// /////////////////////////////////////////////////////////////////////////
// // PROJECT 3 ADDITION ///////////////////////////////////////////////////
// /////////////////////////////////////////////////////////////////////////
test = d3.selectAll('.recipe-checkbox');
console.log(test);

// /* sample code to make your program wait */
// // setTimeout(function(){
// //     test = d3.selectAll('.recipe-checkbox');
// //     console.log(test);

// // }, 5000)

// // 20210312 - added this function becuase checkboxes are created in both buildTable() and refreshTable() functions
function activateTableEventListeners() {
    checkbox = d3.selectAll('.recipe-checkbox');    
    checkbox.on('click', addCheckedData);
    console.log()
};
// /////////////////////////////////////////////////////////////////////////

// // Identify web elements on the page
filterbtn = d3.select('#filter-btn');
weekplanbtn = d3.select('#weekplan-btn');  //////////// PROJECT3 ADDITION
resetbtn = d3.select('#reset-btn');
queryfield = d3.select('#query');
cuisinefield = d3.select('#cuisine');
dietfield = d3.select('#diet');
typeofrecipefield = d3.select('#type_of_recipe');
intolerancesfield = d3.select('#intolerances');


// calories = d3.select('#calories');
// cookingminutesfield = d3.select('#cookingMinutes');

// // Add event listeners to the web elements
filterbtn.on('click', recipemetadataAPIreturn);
weekplanbtn.on('click', addRecipeWeekplan); //////////// PROJECT3 ADDITION
resetbtn.on('click', formReset);
queryfield.on('change', recipemetadataAPIreturn);
cuisinefield.on('change', recipemetadataAPIreturn);
dietfield.on('change', recipemetadataAPIreturn);
typeofrecipefield.on('change', recipemetadataAPIreturn);
intolerancesfield.on('change', recipemetadataAPIreturn);
// calories.on('change', recipemetadataAPIreturn);
// cookingminutesfield.on('change', recipemetadataAPIreturn);


// /////////////////////////////////////////////////////////////////////////
// /////////////////////////////////////////////////////////////////////////
// // AWE SHUCKS NEW NAME!!!! -- ADD VALUES FROM CHECKED BOXES TO GROCERY LIST
// /////////////////////////////////////////////////////////////////////////
// /////////////////////////////////////////////////////////////////////////

console.log('recipeIDs2');
d3.select("#checkbox-btn").on("click", function() {

    console.log('clicked btn');

    recipeIDsToPage2 = [];


    recipeIDs2 = d3.select('#weekplan-table').selectAll('p');
    console.log(recipeIDs2);

    recipeIDs2.each(function() {
        recipeIDsToPage2.push(this.id);
    });

    console.log('this is what you will pass to the next page');
    console.log(recipeIDsToPage2);
    console.log()


    recipe_ids = recipeIDsToPage2.toString();

    // try to go another page
    window.location.href = `/store?recipe_ids=${recipe_ids}`;


});



// /////////////////////////////////////////////////////////////////////////
// /////////////////////////////////////////////////////////////////////////
// // FUNCTION ingredientsAPIreturn()
// /////////////////////////////////////////////////////////////////////////
// /////////////////////////////////////////////////////////////////////////

function ingredientsAPIreturn(selectedRecipeIDs){
    // Create a copy of tableData specifically for filtering
   
    var ingredientsArray = []
    selectedRecipeIDs.forEach(recipeID => {
        d3.json(`/api/ingredients?id=${recipeID}&`, function(ingredientsReturn){
            console.log("---returned ingredients from recipe query--");
            console.log(ingredientsReturn);
            ingredientsArray.push(ingredientsReturn);
            console.log("---should return ingredientsArray---");
            console.log(ingredientsArray);
        });
    });

    
};


// /////////////////////////////////////////////////////////////////////////
// /////////////////////////////////////////////////////////////////////////
// // FUNCTION buildGroceriesTable()
// /////////////////////////////////////////////////////////////////////////
// /////////////////////////////////////////////////////////////////////////
var pricetbody = d3.select('#price-tbody')
// Create function to generate and populate the table
function buildGroceriesTable() {

    // Identify the table and tbody
    var tbody2 = d3.select('#grocery-tbody');


    const urlParams = new URLSearchParams(window.location.search);
    const recipe_ids = urlParams.get('recipe_ids');
    console.log(`page 2:  ${recipe_ids}`);

    var priceTotal = []

    

    // INGREDIENTS DATA API CALL
    d3.json(`/api/getIngredientList?recipe_ids=${recipe_ids}`, function(groceries) {
        console.log(' --- Ingredient data from /api/ingredients --- ')
        console.log(groceries);


        groceries.forEach(record => {
            console.log('this is going in the table');
            console.log(record);
            priceTotal.push(parseInt(record.price))
            var row = tbody2.append('tr');
            ////logic: if checked -- identify the status as checked and if not set status to unchecked; add a status true or flase to records pulled from API
                // function that counts the number of recipes and then assigns an number incrementing by 1
                
                row.append('td').append('input').attr("type", "checkbox").attr('id', `${record['ingredient']}`).attr('class', 'ingredient-checkbox');
                // row.append('td').text(record['recipe_title']);
                row.append('td').text(record['ingredient']);
                // row.append('td').text(record['price']);
                row.append('td').text(record['ingredient_title']);
                // row.append('td').text(record['size']);            
                console.log(record);
    
        });
        var totalSum = d3.sum(priceTotal)
        console.log(totalSum)
        var priceRow = pricetbody.append('tr');
        priceRow.append('td').text(`$${totalSum}`)

    });
   
}

var cardrow = d3.select("#cardrow")

function work() {
    
    const urlParams = new URLSearchParams(window.location.search);
    const recipe_ids = urlParams.get('recipe_ids');
    console.log(`page 2:  ${recipe_ids}`);

    // var test = recipe_ids.split(',');
    // console.log(test);
    // var newTest = [];
    // test.forEach(recipe_id =>{
    //     newTest.push(parseInt(recipe_id))
    // });

    d3.json(`/api/getCards?recipe_ids=${recipe_ids}`, function(recipes){
        recipes.forEach(record => {
            // cardhead.text(record.recipe_title);
            var newColumn = cardrow.append('div').attr("class", "col-lg-3").attr("id", "cardColumn");
            var newCard = newColumn.append('div').attr("class", "card").attr("style", "width: 18rem;");
            newCard.append('img').attr("class", "card-image-top").attr("src", record.image)
            newCard.append('div').attr("class", "card-header").text(record.recipe_title)
            var cardlist = newCard.append('ul').attr("class", "list-group list-group-flush")
            cardlist.append('li').attr("class", "list-group-item").text(`Cooktime: ${record.cooking_minutes} mins`);
            cardlist.append('li').attr("class", "list-group-item").text(`Servings: ${record.servings}`);
            cardlist.append('li').attr("class", "list-group-item").text(record.steps[0]);
            //cardlist.append('button').attr("id", "collapseOne").attr("class", "btn btn-link").attr("data-toggle", "collapse").attr("data-target", "#collapseOne").attr("aria-expanded", "true").attr("aria-controls", "collapseOne").text("Click for Instructions");
            // newCard.append('div').attr("id", "collapseOne").attr("class", "collapseShow").attr("aria-labelledby", "instructionbutton").attr("data-parent", "newCard").text("hi")


            cardrow.append('div').attr("class", "col-sm-1");
            // console.log(record.recipe_steps)
            // console.log("please work")
                    // pic.attr("src", record.image).attr("class", "card-img-top");
            });
            });

}

function herewego () {
    console.log(recipe_ids);
    console.log("here we go")
};

work()
buildGroceriesTable()
