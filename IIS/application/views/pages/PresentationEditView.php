<section class="vh-200 gradient-custom mt-5">
  <div class="container h-100">
    <div class="row d-flex justify-content-center align-items-center h-100">
      <div class="col-12 col-md-8 col-lg-6 col-xl-5">
        <div class="card bg-dark text-white" style="border-radius: 1rem;">
          <div class="card-body p-5 text-center">
            <?php echo form_open_multipart('PresentationController/edit'); ?>
            <div class="mb-md-5 mt-md-4">
              <h2 class="fw-bold mb-2 text-uppercase">Edit presentation</h2>
              <div class="form-outline form-white mb-4">
                <label for="name" class="form-label mt-4">Name</label>
                <input type="text" class="form-control" id="name" name="name" value="<?php echo $presentation["name"] ?>">
                <span class="text-danger"><?php echo form_error('name'); ?></span>
                <small id="name" class="form-text text-muted">Please type name for your presentation</small>
              </div>
              <div class="form-outline form-white mb-4">
                <label for="description" class="form-label mt-4">Description</label>
                <textarea class="form-control" id="description" rows="3" name="description"><?php echo $presentation["description"] ?></textarea>
              </div>
              <div class="form-outline form-white mb-4">
                <label for="description" class="form-label mt-4">Tags</label>
                <textarea class="form-control" id="tags" rows="3" name="tags"><?php echo $presentation["tags"] ?></textarea>
              </div>
              <div class="form-group">
                <label for="formFile" class="form-label mt-4">Image</label>
                <input class="form-control" type="file" name="image" id="image" accept="image/*"><br></br>
            <button class="btn btn-outline-light btn-lg px-5" type="submit" value="<?php echo $id ?>" name="submit">Edit</button>
            <?php form_close(); ?>
          </div>
        </div>
      </div>
    </div>
  </div>
</section>