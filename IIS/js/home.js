window.onload = () => {
	highlightLeftSlots();
};

function highlightLeftSlots() {
	document.querySelectorAll(".ticketsLeft").forEach((e) => {
		let val = parseInt(e.textContent);
		let capacity = parseInt(
			e.parentElement.querySelector(".ticketsCapacity").textContent
		);
		if (val == 0) {
			e.classList.add("text-danger");
		} else if ((val * 100) / capacity < 10) {
			e.classList.add("text-warning");
		}
	});
}

function search() {
	let country = document.querySelector("#countrySelect").value;
	let freeSlots = document.querySelector("#freeSlots").value;
	let from = document.querySelector("#from").value;
	let to = document.querySelector("#to").value;
	let maxPrice = document.querySelector("#priceRange").value;
	let genre = document.querySelector("#genreSelect").value;
	let searchText = document.querySelector("#searchInput").value;
}
