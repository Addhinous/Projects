<section class="vh-200 gradient-custom" style="margin-top: 100px">
  <div class="container h-100">
    <div class="row d-flex justify-content-center align-items-center h-100">
      <div class="col-12 col-md-8 col-lg-6 col-xl-5">
        <div class="card bg-dark text-white" style="border-radius: 1rem;">
          <div class="card-body p-5 text-center">
            <?php echo form_open_multipart('conference/create'); ?>
            <div class="mb-md-5 mt-md-4">
              <h2 class="fw-bold mb-2 text-uppercase">Create a new conference</h2>
              <div class="form-outline form-white mb-4">
                <label for="name" class="form-label mt-4">Name <b class="text-danger">*</b></label>
                <input type="text" class="form-control" id="name" name="name" value="<?php echo set_value('name'); ?>" required>
                <span class="text-danger"><?php echo form_error('name'); ?></span>
                <small id="name" class="form-text text-muted">Please type name for your conference</small>
              </div>
              <div class="form-outline form-white mb-4">
                <label for="genre" class="form-label mt-4">Genre <b class="text-danger">*</b></label>
                <select class="form-select" id="genre" name="genre_id" required>
                  <?php foreach ($genres as $genre) : ?>
                    <option value="<?php echo $genre["id"] ?>" name="genre"> <?php echo $genre["name"] ?> </option>
                  <?php endforeach; ?>
                </select>
                <span class="text-danger"><?php echo form_error('genre_id'); ?></span>
              </div>
              <div class="form-outline form-white mb-4">
                <label for="description" class="form-label mt-4">Description</label>
                <textarea class="form-control" id="description" rows="3" name="description"><?php echo set_value('description'); ?></textarea>
              </div>
              <div class="form-group">
                <label for="formFile" class="form-label mt-4">Image</label>
                <input class="form-control" type="file" name="image" id="image" accept="image/*">
              </div>
              <div class="form-outline form-white mb-4">
                <label for="place" class="form-label mt-4">Place <b class="text-danger">*</b></label>
                <input type="text" class="form-control" id="place" aria-describedby="place" name="place" value="<?php echo set_value('place'); ?>" required>
                <span class="text-danger"><?php echo form_error('place'); ?></span>
                <small id="place" class="form-text text-muted">Please type where your conference takes place</small>
              </div>
              <div class="form-outline form-white mb-4">
                <label for="country" class="form-label mt-4">Country <b class="text-danger">*</b></label>
                <select class="form-select" id="country" name="country_id" required>
                  <?php foreach ($countries as $country) : ?>
                    <option value="<?php echo $country["id"] ?>"> <?php echo $country["name"] ?> </option>
                  <?php endforeach; ?>
                </select>
                <span class="text-danger"><?php echo form_error('genre_id'); ?></span>
              </div>
              <div class="form-outline form-white mb-4">
                <label for="price" class="form-label mt-4">Price <b class="text-danger">*</b></label>
                <input type="number" step="0.1" min="0" class="form-control" id="price" aria-describedby="price" name="price" value="<?php echo set_value('price'); ?>" required>
                <span class="text-danger"><?php echo form_error('price'); ?></span>
                <small id="price" class="form-text text-muted">Please type ticket price in $</small>
              </div>
              <div class="form-outline form-white mb-4">
                <!-- Date input -->
                <label class="control-label" for="from">Date from <b class="text-danger">*</b></label>
                <input class="form-control" id="from" type="datetime-local" name="from" value="<?php echo set_value('from'); ?>" required>
                <span class="text-danger"><?php echo form_error('from'); ?></span>
              </div>
            </div>
            <div class="form-outline form-white mb-4">
              <!-- Date input -->
              <label class="control-label" for="to">Date until <b class="text-danger">*</b></label>
              <input class="form-control" id="to" type="datetime-local" name="to" value="<?php echo set_value('to'); ?>" required>
              <span class="text-danger"><?php echo form_error('to'); ?><?php echo $this->session->flashdata('date_error'); ?><?php echo $this->session->flashdata('capacity_error'); ?></span>

            </div>

            <div class="form-outline form-white mb-4">
              <label for="capacity" class="form-label mt-4">Capacity <b class="text-danger">*</b></label>
              <input type="number" min="0" class="form-control" id="capacity" aria-describedby="capacity" name="capacity" value="<?php echo set_value('capacity'); ?>" required>
              <span class="text-danger"><?php echo form_error('capacity'); ?></span>
              <small id="capacity" class="form-text text-muted">Please type maximum conference capacity</small>
            </div>


            <button class="btn btn-outline-light btn-lg px-5" type="submit" name="submit">Create</button>
            <?php form_close(); ?>
          </div>
        </div>
      </div>
    </div>
  </div>
</section>