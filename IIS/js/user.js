let userToEditId;
let modalEditErr = { email: 0, name: 0, surename: 0 };
let modalEditMeErr = { email: 0, name: 0, surename: 0, changePass: 0 };
let ajaxPath = "";

window.onload = () => {
	addListeners();
};

function validate_modalEditErr() {
	return (
		modalEditErr.email == 0 &&
		modalEditErr.name == 0 &&
		modalEditErr.surename == 0
	);
}

function validate_password(val) {
	return (
		val.length >= 6 &&
		/[a-z]/.test(val) &&
		/[A-Z]/.test(val) &&
		/[0-9]/.test(val)
	);
}

function validate_password_form() {
	if (modalEditMeErr.changePass) {
		return (
			validate_password(document.querySelector("#modalMyNewPassword").value) &&
			document.querySelector("#modalMyNewPassword").value ==
				document.querySelector("#modalMyNewPasswordAgain").value
		);
	}
	return true;
}

function validate_modalEditMeErr() {
	return (
		modalEditMeErr.email == 0 &&
		modalEditMeErr.name == 0 &&
		modalEditMeErr.surename == 0 &&
		validate_password_form()
	);
}

function search() {
	let value = document.querySelector("#usersFilter").value.toLocaleLowerCase();
	Array.from(document.querySelectorAll("#usersTbody tr")).map((e) => {
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

function addListeners() {
	//validate my personal data
	document.querySelector("#modalInputMyEmail").addEventListener("input", () => {
		validate_modalInputMyEmail();
	});
	document.querySelector("#modalInputMyName").addEventListener("input", () => {
		validate_modalInputMyName();
	});
	document
		.querySelector("#modalInputMySurename")
		.addEventListener("input", () => {
			validate_modalInputMySurename();
		});

	document
		.querySelectorAll("#modalMyNewPassword, #modalMyNewPasswordAgain")
		.forEach((item) => {
			item.addEventListener("input", function () {
				document.querySelector("#editMeSubmit").disabled =
					!validate_modalEditMeErr();
			});
		});

	document
		.querySelector("#modalMyNewPassword")
		.addEventListener("input", function () {
			if (validate_password(this.value)) {
				this.classList.remove("is-invalid");
			} else {
				this.classList.add("is-invalid");
			}
			validate_modalInputMyPasswordAgain();
		});

	document
		.querySelector("#modalMyNewPasswordAgain")
		.addEventListener("input", function () {
			validate_modalInputMyPasswordAgain();
		});

	document
		.querySelector("#modalChangePassword")
		.addEventListener("change", function () {
			modalEditMeErr.changePass = this.checked;
			document.querySelector("#editMeSubmit").disabled =
				!validate_modalEditMeErr();
			document.querySelector("#modalMyOldPassword").disabled = !this.checked;
			document.querySelector("#modalMyNewPassword").disabled = !this.checked;
			document.querySelector("#modalMyNewPasswordAgain").disabled =
				!this.checked;
		});
	document.querySelector("#usersFilter").addEventListener("input", () => {
		search();
	});
	// validate input for editing users
	document.querySelector("#modalInputEmail").addEventListener("input", (e) => {
		if (validateEmail(e.target.value)) {
			e.target.classList.remove("is-invalid");
			modalEditErr.email = 0;
			document.querySelector("#editSubmit").disabled = !validate_modalEditErr();
		} else {
			e.target.classList.add("is-invalid");
			modalEditErr.email = 1;
			document.querySelector("#editSubmit").disabled = true;
		}
	});
	document.querySelector("#modalInputName").addEventListener("input", (e) => {
		if (e.target.value.length > 0) {
			e.target.classList.remove("is-invalid");
			modalEditErr.name = 0;
			document.querySelector("#editSubmit").disabled = !validate_modalEditErr();
		} else {
			e.target.classList.add("is-invalid");
			modalEditErr.name = 1;
			document.querySelector("#editSubmit").disabled = true;
		}
	});
	document
		.querySelector("#modalInputSurename")
		.addEventListener("input", (e) => {
			if (e.target.value.length > 0) {
				e.target.classList.remove("is-invalid");
				modalEditErr.surename = 0;
				document.querySelector("#editSubmit").disabled =
					!validate_modalEditErr();
			} else {
				e.target.classList.add("is-invalid");
				modalEditErr.surename = 1;
				document.querySelector("#editSubmit").disabled = true;
			}
		});
}

function validate_modalInputMyPasswordAgain() {
	ele = document.querySelector("#modalMyNewPasswordAgain");
	if (ele.value == document.querySelector("#modalMyNewPassword").value) {
		ele.classList.remove("is-invalid");
	} else {
		ele.classList.add("is-invalid");
	}
}

function validate_modalInputMyName() {
	let ele = document.querySelector("#modalInputMyName");
	if (ele.value.length > 0) {
		ele.classList.remove("is-invalid");
		modalEditMeErr.name = 0;
		document.querySelector("#editMeSubmit").disabled =
			!validate_modalEditMeErr();
	} else {
		ele.classList.add("is-invalid");
		modalEditMeErr.name = 1;
		document.querySelector("#editMeSubmit").disabled = true;
	}
}

function validate_modalInputMyEmail() {
	let ele = document.querySelector("#modalInputMyEmail");
	if (validateEmail(ele.value)) {
		ele.classList.remove("is-invalid");
		modalEditMeErr.email = 0;
		document.querySelector("#editMeSubmit").disabled =
			!validate_modalEditMeErr();
	} else {
		ele.classList.add("is-invalid");
		modalEditMeErr.email = 1;
		document.querySelector("#editMeSubmit").disabled = true;
	}
}

function validate_modalInputMySurename() {
	let ele = document.querySelector("#modalInputMySurename");
	if (ele.value.length > 0) {
		ele.classList.remove("is-invalid");
		modalEditMeErr.surename = 0;
		document.querySelector("#editMeSubmit").disabled =
			!validate_modalEditMeErr();
	} else {
		ele.classList.add("is-invalid");
		modalEditMeErr.surename = 1;
		document.querySelector("#editMeSubmit").disabled = true;
	}
}

function editUserModal(id) {
	userToEditId = id;
	modalEditErr = { email: 0, name: 0, surename: 0 };
	document.querySelector("#editMeSubmit").disabled = false;
	document
		.querySelectorAll("#userEditModal input")
		.forEach((e) => e.classList.remove("is-invalid"));

	var formData = new FormData();
	formData.append("id", id);
	fetch(ajaxPath + "ajax-getUserById", {
		method: "POST",
		body: formData,
	})
		.then(function (response) {
			return response.json();
		})
		.then(function (data) {
			editUserModalInsertData(data);
		});
}

function editMeModal() {
	modalEditMeErr = { email: 0, name: 0, surename: 0, changePass: 0 };
	document.querySelector("#editMeSubmit").disabled = false;
	document
		.querySelectorAll("#userEditMeModal input")
		.forEach((e) => e.classList.remove("is-invalid"));

	fetch(ajaxPath + "ajax-getUserBySession", {
		method: "POST",
	})
		.then(function (response) {
			return response.json();
		})
		.then(function (data) {
			editMeModalInsertData(data);
		});
}

function editMeModalInsertData(data) {
	document.querySelector("#modalInputMyEmail").value = data.email;
	document.querySelector("#modalInputMyName").value = data.name;
	document.querySelector("#modalInputMySurename").value = data.surename;
}

function editUserModalInsertData(data) {
	userToEditId = data.id;
	document.querySelector("#modalInputEmail").value = data.email;
	document.querySelector("#modalInputName").value = data.name;
	document.querySelector("#modalInputSurename").value = data.surename;
	document.querySelector("#modalCheckboxAdmin").checked = data.is_admin == "1";
	document.querySelector("#modalCheckboxDeactivated").checked =
		data.is_deactivated == "1";
}

function editUserModalSubmit() {
	let email = document.querySelector("#modalInputEmail").value;
	let name = document.querySelector("#modalInputName").value;
	let surename = document.querySelector("#modalInputSurename").value;
	let admin = document.querySelector("#modalCheckboxAdmin").checked ? "1" : "0";
	let deactivated = document.querySelector("#modalCheckboxDeactivated").checked
		? "1"
		: "0";

	var formData = new FormData();
	console.log(userToEditId);
	formData.append("id", userToEditId);
	formData.append("email", email);
	formData.append("name", name);
	formData.append("surename", surename);
	formData.append("admin", admin);
	formData.append("deactivated", deactivated);

	fetch(ajaxPath + "ajax-updateUserById", {
		method: "POST",
		body: formData,
	})
		.then(function (response) {
			return response.json();
		})
		.then(function (data) {
			if (data == "err-email") {
				document.querySelector("#modalInputEmail").classList.add("is-invalid");
				return;
			}
			$("#userEditModal").modal("hide");
			userToEditId = undefined;
			editUsersUpdateTable(data);
		});
}

function editUsersUpdateTable(data) {
	let html = "";
	modalEditErr = 0;
	data.forEach((e) => {
		let style = parseInt(e.is_deactivated) ? 'style="color: red"' : "";
		let email = parseInt(e.is_admin)
			? e.email + ' <span style="color: #00ffb8">(admin)</span>'
			: e.email;
		let conferenceStyle =
			parseInt(e.conferences) == 0 ? 'style="color: grey"' : "";
		let presentationsStyle =
			parseInt(e.presentations) == 0 ? 'style="color: grey"' : "";
		html += `
		<tr>
			<th scope="row" ${style}>${email}</th>
			<td>${e.name}</td>
			<td>${e.surename}</td>
			<td ${conferenceStyle}>${e.conferences}</td>
			<td ${presentationsStyle}>${e.presentations}</td>
			<td>
				<a
					href=""
					data-bs-toggle="modal"
					onclick="editUserModal(${e.id} )"
					data-bs-target="#userEditModal"
				>
					Edit
				</a>
			</td>
		</tr>`;
	});
	document.querySelector("#usersTbody").innerHTML = html;
}

function validateEmail(email) {
	const re =
		/^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
	return re.test(email);
}

function deleteUserModalSubmit() {
	var conf = confirm("Do you really want to delete this user?");
	if (conf) {
		var formData = new FormData();
		formData.append("id", userToEditId);
		userToEditId = undefined;

		fetch(ajaxPath + "ajax-deleteUserById", {
			method: "POST",
			body: formData,
		})
			.then(function (response) {
				return response.json();
			})
			.then(function (data) {
				editUsersUpdateTable(data);
			});
	}
}

function editUserMeModalSubmit() {
	let email = document.querySelector("#modalInputMyEmail").value;
	let name = document.querySelector("#modalInputMyName").value;
	let surename = document.querySelector("#modalInputMySurename").value;
	let changePass = document.querySelector("#modalChangePassword").checked;
	let oldPass = document.querySelector("#modalMyOldPassword").value;
	let newPass = document.querySelector("#modalMyNewPassword").value;

	var formData = new FormData();
	formData.append("email", email);
	formData.append("name", name);
	formData.append("surename", surename);
	formData.append("changepass", changePass);
	formData.append("oldpass", oldPass);
	formData.append("newpass", newPass);

	fetch(ajaxPath + "ajax-updateUserInfoById", {
		method: "POST",
		body: formData,
	})
		.then(function (response) {
			return response.json();
		})
		.then(function (data) {
			if (data == "err-pass") {
				document.querySelector("#modalMyOldPassword").value = "";
				document
					.querySelector("#modalMyOldPassword")
					.classList.add("is-invalid");
			} else if (data == "err-email") {
				document
					.querySelector("#modalInputMyEmail")
					.classList.add("is-invalid");
			} else {
				document.querySelector("#userEditMeModal input").forEach((e) => {
					e.classList.remove("is-invalid");
					e.id == "modalChangePassword" ? (e.checked = false) : (e.value = "");
				});
				document.querySelector("#userEditMeModalCloseBtn").click();
				document.querySelector("#alertChangedUserInforamtions").style.display =
					"block";
				document.querySelector("#editMeSubmit").disabled = true;
			}
		});
}
