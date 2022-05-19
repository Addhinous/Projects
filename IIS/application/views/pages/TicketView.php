<section class="vh-100 gradient-custom">
  <div class="container h-100">
    <div class="row d-flex justify-content-center align-items-center h-100">
      <div class="col-12 col-md-8 col-lg-6 col-xl-5">
        <div class="card bg-dark text-white" style="border-radius: 1rem;">
          <div class="card-body p-5 text-center">
            <div class="mb-md-5 mt-md-4">
              <h3 class="fw-bold mb-2">Details of your reservation</h3><br></br>
              <div style="text-align: left">
                <p>Name on reservation: <?php echo $name ." ". $surename; ?></p>
                <p>Number of tickets: <?php echo $num_tickets; ?></p>
                <p>Code of reservation: <?php echo $code; ?></p>
                <p>Email: <?php echo $email; ?></p>
              </div><br></br>
              <a href="<?php echo base_url(); ?>">
                <button type="button" class="btn btn-primary btn-lg">Home</button>
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</section>