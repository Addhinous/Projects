<script>

var filters = {"price" : false,
              "slots" : false,
              "from" : false,
              "to" : false,
              "country" : false,
              "genre" : false,
              };

function filter(filter_function){

    switch(filter_function) {
        case "price":
            filters["price"] = true;
            break;
        case "slots":
            filters["slots"] = true;
            break;
        case "from":
            filters["from"] = true;
            break;
        case "to":
            filters["to"] = true;
            break;
        case "country":
            filters["country"] = true;
            break;
        case "genre":
            filters["genre"] = true;
            break;
        default:
            break;
    }

    conferences = document.getElementsByClassName("card cards-devices");
    
    for (i = 0; i < conferences.length; i++) {
        conferences[i].style.display = "inline-block";
    }

    if(filters["price"] == true){
        filterMaxPrice();
    }

    if(filters["slots"] == true){
        filterFreeSlots();
    }

    if(filters["from"] == true || filters["to"] == true){
        filterDateRange();
    }

    if(filters["country"] == true){
        filterCountry();
    }

    if(filters["genre"] == true){
        filterGenre();
    }
}

function myFunction() {
  var input, filter, conferences, conference_name;
  input = document.getElementById('searchInput');
  filter = input.value.toUpperCase();
  conferences = document.getElementsByClassName("card cards-devices");
  
  for (i = 0; i < conferences.length; i++) {
    conferences[i].style.display = "inline-block";
    conference_name = conferences[i].getElementsByClassName("card-header")[0].textContent;
    
    if(!conference_name.toUpperCase().includes(filter)){
        conferences[i].style.display = "none";
    }
  }
}

function filterGenre(){

    var filter_genres = [];
    var filter_genre, conferences, conference_genre;

    for (var filter_genre of document.getElementById('genreSelect').options)
    {
        if (filter_genre.selected) {
            filter_genres.push(filter_genre.value);
        }
    }

    conferences = document.getElementsByClassName("card cards-devices");
    for (i = 0; i < conferences.length; i++) {

        if(filter_genres.length == 0 || filter_genres[0] == "-"){
            return;
        }

        conference_genre = conferences[i].getElementsByClassName("list-group-item genres")[0].textContent.split(" ")[1];

        var c = false;;
        for(var j = 0 ; j < filter_genres.length ; j++){
            if(!conference_genre.localeCompare(filter_genres[j])){
                c = true;
            }
        }
        if(c == false){
            conferences[i].style.display = "none";
        }
    }
}

function filterCountry(){

var filter_countries = [];
var filter_country, conferences, conference_country;

for (var filter_country of document.getElementById('countrySelect').options)
{
    if (filter_country.selected) {
        filter_countries.push(filter_country.value);
    }
}

conferences = document.getElementsByClassName("card cards-devices");
for (i = 0; i < conferences.length; i++) {

    if(filter_countries.length == 0 || filter_countries[0] == "-"){
        return;
    }

    conference_country = conferences[i].getElementsByClassName("card-subtitle text-muted country")[0].textContent;

    var c = false;
    for(var j = 0 ; j < filter_countries.length ; j++){
        if(!conference_country.localeCompare(filter_countries[j])){
                c = true;
        }
    }

        if(c == false){
            conferences[i].style.display = "none";
        }
}
}

function filterMaxPrice(){

    var max_price, conferences, conference_price;
    max_price = parseFloat(document.getElementById("priceRange").value);

    conferences = document.getElementsByClassName("card cards-devices");

    for (i = 0; i < conferences.length; i++) {
        conference_price = conferences[i].getElementsByClassName("list-group list-group-flush price")[0].getElementsByClassName("list-group-item price")[0].textContent;
        conference_price = parseFloat(conference_price.split(" ")[1].trim());

        if(conference_price > max_price){
            conferences[i].style.display = "none";
        }
    }
}

function filterFreeSlots(){

    var slots, conferences, free_slots;
    slots = parseInt(document.getElementById("freeSlots").value);
    conferences = document.getElementsByClassName("card cards-devices");
    for (i = 0; i < conferences.length; i++) {

        free_slots = conferences[i].getElementsByClassName("list-group list-group-flush tickets_left")[0];
        free_slots = free_slots.getElementsByClassName("list-group-item tickets_left")[0].textContent;
        free_slots = parseInt(free_slots.split(" ")[2].split("/")[0]);

        if(slots > free_slots){
            conferences[i].style.display = "none";
        }
    }
}

function filterDateRange(){

    var from_filter, until_filter, from, until, conferences;

    from_filter = new Date(document.getElementById("from").value);
    until_filter = new Date(document.getElementById("to").value);

    conferences = document.getElementsByClassName("card cards-devices");

    for (i = 0; i < conferences.length; i++) {

        from = conferences[i].getElementsByClassName("card-subtitle text-muted dateRange")[0].textContent.split("-");
        until = new Date(from[1].trim());
        from = new Date(from[0].trim());

        if(!isNaN(from_filter.getTime())){
            if(from_filter.getTime() > from.getTime()){
                conferences[i].style.display = "none";
            }
        }

        if(!isNaN(until_filter.getTime())){
            if(until_filter.getTime() < until.getTime()){
                conferences[i].style.display = "none";
            }
        }
    }
}

</script>

<script type='text/javascript' src="<?php echo base_url(); ?>js/home.js"></script>
<?php if ($justloggedin) : ?>
    <div class="alert alert-dismissible alert-success">
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        <strong>successfully logged in</strong>.
    </div>
<?php endif; ?>
<?php if (isset($_SESSION["login_error_deactivated"])) : ?>
    <div class="alert alert-dismissible alert-danger">
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        <strong>Account is deactivated, contact administrator</strong>.
    </div>
<?php endif; ?>

<!-- ROWS -->
<div class="dropdown" style="float:left">
    <a class="nav-link dropdown-toggle" data-bs-toggle="dropdown" href="#" role="button" aria-haspopup="true" aria-expanded="false" style="color:rgba(255,255,255,.6);" data-keepOpenOnClick>Filters</a>
    <div class="dropdown-menu dropdown-multicol" style="width: 300px; margin-left: 10px;" data-keepOpenOnClick>
        <div class="dropdown-row" style="margin-left: 2%">
        <div style="float:left">
                <label for="priceRange" class="form-label mt-4">Maximum price</label>
                <input type="number" min="0" step="0.01" class="form-control" id="priceRange"  onkeyup="filter('price');" style="width: 120px">
            </div>
            <div style="margin-left: 135px">
                <label for="freeSlots" class="form-label mt-4">Free slots</label>
                <input type="number" min="0" class="form-control" id="freeSlots" onkeyup="filter('slots');" style="width: 120px">
            </div>
        </div>

        <div class="dropdown-row" style="margin-left: 2%;">
            <div style="float:left">
                <label for="from" class="form-label mt-4">From</label>
                <input type="date" class="form-control" id="from" style="width: 120px" onchange="filter('from');">
            </div>
            <div style="margin-left: 135px">
                <label for="to" class="form-label mt-4">To</label>
                <input type="date" class="form-control" id="to" style="width: 120px" onchange="filter('to');">
            </div>
        </div>

        <div class="dropdown-row" style="margin-left: 2%;">
        <div style="float:left">
                <label for="countrySelect" class="form-label mt-4">Country</label>
                <select multiple class="form-select" id="countrySelect" style="width: 120px" onchange="filter('country');">
                    <option selected>-</option>
                    <?php foreach ($countries as $country) : ?>
                        <option><?php echo $country["name"] ?></option>
                    <?php endforeach; ?>
                </select>
            </div>
            <div style="margin-left: 135px">
                <label for="genreSelect" class="form-label mt-4">Genre</label>
                <select class="form-select" multiple id="genreSelect" style="width: 120px" onchange="filter('genre');">
                    <option selected>-</option>
                    <?php foreach ($genres as $genre) : ?>
                        <option><?php echo $genre["name"] ?></option>
                    <?php endforeach; ?>
                </select>
            </div>
        </div>
        

        <!-- element pre Matejka -->
        <!-- <div class="dropdown-row" style="margin-left: 2%;" >
            <div style="float:left">
                <label for="genreSelect" class="form-label mt-4">Genre</label>
                <select class="form-select" id="genreSelect" style="width: 120px">
                <option selected>-</option>
                <?php foreach ($genres as $genre) : ?>
                   <option><?php echo $genre["name"] ?></option>
                <?php endforeach; ?>
                </select>
            </div>
            <div style="margin-left: 135px">
                <label for="genreSelect" class="form-label mt-4">Genre</label>
                <select class="form-select" id="genreSelect" style="width: 120px">
                <option selected>-</option>
                <?php foreach ($genres as $genre) : ?>
                   <option><?php echo $genre["name"] ?></option>
                <?php endforeach; ?>
                </select>
            </div>
        </div>            -->
    </div>

</div>
<div style="margin-top: 85px;">
    <input class="form-control me-sm-2" type="text" id="searchInput" placeholder="Search" style="width: 40%; margin-left: 2%; float:left">
    <button class="btn btn-secondary my-sm-0" style="margin-left: 40px" onclick="myFunction()">Search</button>
</div>

<br /><br />

<div>
    <?php foreach ($conferences as $conf) : ?>
        <div class="card cards-devices">
            <h4 class="card-header"><?php echo $conf["name"] ?></h3>
                <div class="card-body">
                    <h5 class="card-title"><?php echo $conf["place"] ?>
            </h4>
            <h6 class="card-subtitle text-muted dateRange"><?php echo date("Y/m/d",strtotime($conf["from"])) . " - " . date("Y/m/d",strtotime($conf["to"])) ?></h6>
            <br>
            <h6 class="card-subtitle text-muted country"><?php echo $conf["country"]->name ?></h6>
        </div>
        <?php if ($conf["image"] == "") : ?>
            <svg xmlns="http://www.w3.org/2000/svg" class="d-block user-select-none" width="100%" height="200" aria-label="Placeholder: Image cap" focusable="false" role="img" preserveAspectRatio="xMidYMid slice" viewBox="0 0 318 180" style="font-size:1.125rem;text-anchor:middle">
                <rect width="100%" height="100%" fill="#868e96"></rect>
                <text x="50%" y="50%" fill="#dee2e6" dy=".3em">No image</text>
            </svg>
        <?php else : ?>
            <div style="height: 200px; width: 353px;">
                <img src="<?php echo "uploads/" . $conf["image"] ?>" class="img-fluid" alt="Responsive image" style="max-width: 100%; max-height: 100%; margin: auto; display: block;">
            </div>
        <?php endif; ?>
        <ul class="list-group list-group-flush price">
            <li class="list-group-item price">Price: <?php echo $conf["price"] ?> $</li>
        </ul>
        <ul class="list-group list-group-flush tickets_left">
            <li class="list-group-item tickets_left">Tickets left: <?php echo '<span class="ticketsLeft">' . $conf["left"] . '</span>/<span class="ticketsCapacity" >' . $conf["capacity"] . "</span>" ?></li>
        </ul>
        <ul class="list-group list-group-flush tickets_left">
            <li class="list-group-item genres">Genre: <?php echo $conf["genre"]["name"] ?> </li>
        </ul>
        <div class="card-body">
            <a href=<?php echo '"' . base_url() . 'conference?id=' . $conf["id"] . '"' ?> class="card-link">Show details</a>
        </div>
        <div class="card-footer text-muted">
        </div>
</div>
<?php endforeach; ?>
</div>