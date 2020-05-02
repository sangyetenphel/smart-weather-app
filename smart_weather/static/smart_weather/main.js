$(document).ready(function(){
    $("#exampleModal").on('shown.bs.modal', function(){
        $(this).find('#search').focus();
    });
});

const search = document.getElementById('search');
const matchList = document.getElementById('match-list');
let cities;

// Get cities
const getCities = async () => {
    const res = await fetch('../static/smart_weather/cleaned_city.list.json'); 
    cities = await res.json();
};

// Filter Cities
const searchCities = searchText => {
    // Get matches to current text input
    let matches = cities.filter(city => {
        const regex = new RegExp(`^${searchText}`, 'gi');
        return city.name.match(regex) || city.state.match(regex);
    }); 

    // Clear when input or matches are empty
    if (searchText.length === 0) {
        matches = [];
        matchList.innerHTML = '';
    }

    outputHtml(matches);
};

// Show results in HTML
const outputHtml = matches => {
    if (matches.length > 0){
        const html = matches.map(
            match => `
            <div class="card card-body mb-1">
                <a href="${match.id}"><h4>${match.name} ${match.state} ${
                    match.country
                }</span></h4></a>
            </div> 
            `
        ).join('');

        matchList.innerHTML = html;
    }
}

window.addEventListener('DOMContentLoaded', getCities);
search.addEventListener('input', () => searchCities(search.value));