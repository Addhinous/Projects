<script>

function post() {

const form2 = document.createElement('form');
form2.method = 'post';
form2.action = 'userAccessController/registration?conference_id=' + "<?php echo $_GET['reserve']?>";

var params = [];
params.push({"type" : "hidden", "name" : "name", "value" : document.getElementById("name").value});
params.push({"type" : "hidden", "name" : "surename", "value" : document.getElementById("surename").value});
params.push({"type" : "hidden", "name" : "email", "value" : document.getElementById("email").value});



for (var i = 0 ; i < params.length ; i++) {
    const hiddenField = document.createElement('input');
    hiddenField.type = params[i]["type"];
    hiddenField.name = params[i]["name"];
    hiddenField.value = params[i]["value"];
    form2.appendChild(hiddenField);
}

document.body.appendChild(form2);
form2.submit();
}

</script>

<section class="vh-100 gradient-custom">
  <div class="container h-100">
    <div class="row d-flex justify-content-center align-items-center h-100">
      <div class="col-12 col-md-8 col-lg-6 col-xl-5">
        <div class="card bg-dark text-white" style="border-radius: 1rem;">
          <div class="card-body p-5 text-center">
            
            <div class="mb-md-5 mt-md-4">
              <h3 class="fw-bold mb-2">Please, fill out the details for your reservation</h3>

              <?php echo form_open('ReservationController/reserveTickets?reserve=' . $_GET["reserve"]); ?>
                <div class="form-outline form-white mb-4" style="margin:auto; width: 180px">
                  <input type="number" min="1" class="form-control" id="num_tickets" name="num_tickets" aria-describedby="emailHelp" style="width: 180px; text-align: center" value="1">
                  <label class="form-label" for="num_tickets" style="">Number of tickets<b class="text-danger">*</b></label>
                </div>
                <div class="form-outline form-white mb-4">
                    <input type="text" id="name" name="name" class="form-control form-control-lg" value="">
                    <span class="text-danger"></span>
                    <label class="form-label" for="name">Name<b class="text-danger">*</b></label>
                </div>

                <div class="form-outline form-white mb-4">
                    <input type="text" id="surename" name="surename" class="form-control form-control-lg" value="">
                    <span class="text-danger"></span>
                    <label class="form-label" for="surename">Surename<b class="text-danger">*</b></label>
                </div>

                <div class="form-outline form-white mb-4">
                    <input type="email" id="email" name="email" class="form-control form-control-lg" value="">
                    <span class="text-danger"></span>
                    <label class="form-label" for="email">Email<b class="text-danger">*</b></label>
                </div>

                <div>
                  <p class="mb-0">Register to simplify the reservation process <a type="submit" name="submit" onclick="post();" class="text-white-50 fw-bold">Register now</a></p>
                </div>

                <p class="small mb-5 pb-lg-2"><a class="text-white-50" href="#!"></a></p>

                <button class="btn btn-outline-light btn-lg px-5" type="submit" name="submit">Reserve tickets</button>
                <p class="text-danger" style="margin-top: 10px"><?php echo $this->session->flashdata('number_error'); ?></p>
              <?php form_close();?>
            </div>
            
          </div>
        </div>
      </div>
    </div>
  </div>
</section>