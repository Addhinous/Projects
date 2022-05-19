window.onload = () => {
	addListeners();
};

let ajaxPath;
function removePlanItem(ele, id) {
	var formData = new FormData();
	formData.append("id", id);

	fetch(ajaxPath + "ajax-managerDeletePlan", {
		method: "POST",
		body: formData,
	}).then(function (response) {
		ele.parentElement.parentElement.remove();
	});
}

function removeResrvationsByCode(ele, code) {
	var formData = new FormData();
	formData.append("code", code);

	fetch(ajaxPath + "ajax-managerDeleteTicketByCode", {
		method: "POST",
		body: formData,
	}).then(function (response) {
		ele.parentElement.parentElement.remove();
	});
}

function deleteRoomById(ele, id) {
	var formData = new FormData();
	formData.append("id", id);

	fetch(ajaxPath + "ajax-managerDeleteRoomById", {
		method: "POST",
		body: formData,
	})
		.then(function (response) {
			return response.json();
		})
		.then(function (data) {
			if (data == "ok") {
				ele.parentElement.parentElement.remove();
			} else {
				alert("there are presentations in this room");
			}
		});
}

function addListeners() {
	document.querySelector("#roomsFilter").addEventListener("input", () => {
		roomSearch();
	});

	document.querySelector("#presentationsFilter").addEventListener("input", () => {
		presentationSearch();
	});

	document.querySelector("#reservationsFilter").addEventListener("input", () => {
		reservationSearch();
	});
}

function roomSearch() {
	let value = document.querySelector("#roomsFilter").value.toLocaleLowerCase();
	Array.from(document.querySelectorAll("#roomsTbody tr")).map((e) => {
		e = e.querySelectorAll("td, th");
		for (let i = 0; i < e.length - 1; i++) {
			if (e[i].textContent.toLocaleLowerCase().trim().includes(value.trim())) {
				e[i].parentElement.style.display = "table-row";
				break;
			}
			e[i].parentElement.style.display = "none";
		}
	});
}

function reservationSearch() {
	let value = document.querySelector("#reservationsFilter").value.toLocaleLowerCase();
	Array.from(document.querySelectorAll("#reservationsTbody tr")).map((e) => {
		e = e.querySelectorAll("td, th");
		for (let i = 0; i < e.length - 1; i++) {
			if (e[i].textContent.toLocaleLowerCase().trim().includes(value.trim())) {
				e[i].parentElement.style.display = "table-row";
				break;
			}
			e[i].parentElement.style.display = "none";
		}
	});
}

function presentationSearch() {
	let value = document.querySelector("#presentationsFilter").value.toLocaleLowerCase();
	Array.from(document.querySelectorAll("#presentationsTbody tr")).map((e) => {
		e = e.querySelectorAll("td, th");
		for (let i = 0; i < e.length - 1; i++) {
			if (e[i].textContent.toLocaleLowerCase().trim().includes(value.trim())) {
				e[i].parentElement.style.display = "table-row";
				break;
			}
			e[i].parentElement.style.display = "none";
		}
	});
}
