<section class="vh-100 gradient-custom">
  <div class="container h-100">
    <div class="row d-flex justify-content-center align-items-center h-100">
      <div class="col-12 col-md-8 col-lg-6 col-xl-5">
        <div class="card bg-dark text-white" style="border-radius: 1rem;">
          <div class="card-body p-5 text-center">

            <div class="mb-md-5 mt-md-4">
              <h2 class="fw-bold mb-2 text-uppercase">Registration</h2>
              <p class="text-white-50 mb-5">Please enter your login and password!</p>
              <?php echo form_open('userAccessController/' . $url); ?>
              <div class="form-outline form-white mb-4">
                <input type="email" id="typeEmail" name="email" class="form-control form-control-lg" value="<?php echo set_value('email'); ?>">
                <span class="text-danger"><?php echo form_error('email'); ?></span>
                <label class="form-label" for="typeEmail">Email <b class="text-danger">*</b></label>
              </div>
              <div class="form-outline form-white mb-4">
                <input type="text" id="typeName" name="name" class="form-control form-control-lg" value="<?php echo set_value('name'); ?>">
                <span class="text-danger"><?php echo form_error('name'); ?></span>
                <label class="form-label" for="typeName">Name <b class="text-danger">*</b></label>
              </div>
              <div class="form-outline form-white mb-4">
                <input type="text" id="typeSurename" name="surename" class="form-control form-control-lg" value="<?php echo set_value('surename'); ?>">
                <span class="text-danger"><?php echo form_error('surename'); ?></span>
                <label class="form-label" for="typeSurename">Surename <b class="text-danger">*</b></label>
              </div>
              <div class="form-outline form-white mb-4">
                <input type="password" id="typePassword" name="password" class="form-control form-control-lg">
                <span class="text-danger"><?php echo form_error('password'); ?></span>
                <label class="form-label" for="typePassword">Password <b class="text-danger">*</b></label>
              </div>
              <div class="form-outline form-white mb-4">
                <input type="password" id="typePasswordAgain" name="passwordAgain" class="form-control form-control-lg">
                <span class="text-danger"><?php echo form_error('passwordAgain'); ?></span>
                <label class="form-label" for="typePasswordAgain">Password again <b class="text-danger">*</b></label>
              </div>

              <?php if (isset($_GET["conference_id"])) { ?>
                <input type="hidden" id="conference_id" name="conference_id" class="form-control form-control-lg" value="<?php echo $_GET["conference_id"] ?>">
              <?php } ?>

              <button class="btn btn-outline-light btn-lg px-5" type="submit" name="submit">Sign Up</button>
              <p class="text-danger"><?php echo $this->session->flashdata('registration_error'); ?></p>
              <?php form_close(); ?>
            </div>

            <div>
              <p class="mb-0">Already have an account? <a href=<?php echo site_url('UserAccessController/login'); ?> class="text-white-50 fw-bold">Login</a></p>
            </div>

          </div>
        </div>
      </div>
    </div>
  </div>
</section>