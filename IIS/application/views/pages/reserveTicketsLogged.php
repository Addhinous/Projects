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
                  <label class="form-label" for="num_tickets" style="">Number of tickets</label>
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