<?php if (isset($_SESSION["success"])) : ?>
    <div class="alert alert-dismissible alert-success">
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        <strong>Room created successfully</strong>.
    </div>
<?php endif; ?>
<section class="vh-200 gradient-custom" style="margin-top: 100px">
    <div class="container h-100">
        <div class="row d-flex justify-content-center align-items-center h-100">
            <div class="col-12 col-md-8 col-lg-6 col-xl-5">
                <div class="card bg-dark text-white" style="border-radius: 1rem;">
                    <div class="card-body p-5 text-center">
                        <?php echo form_open_multipart('roomsController/create'); ?>
                        <div class="mb-md-5 mt-md-4">
                            <h2 class="fw-bold mb-2 text-uppercase">Create room</h2>
                            <div class="form-outline form-white mb-4">
                                <label for="name" class="form-label mt-4">Name <b class="text-danger">*</b></label>
                                <input type="text" class="form-control" id="name" name="name" value="<?php echo set_value('name'); ?>" required>
                                <span class="text-danger"><?php echo form_error('name'); ?></span>
                            </div>
                            <div class="form-outline form-white mb-4">
                                <label for="description" class="form-label mt-4">Description</label>
                                <textarea class="form-control" id="description" rows="3" name="description"><?php echo set_value('description'); ?></textarea>
                            </div>
                            <div class="form-group">
                                <label for="city" class="form-label mt-4">City <b class="text-danger">*</b></label>
                                <input type="text" class="form-control" id="city" name="city" value="<?php echo set_value('city'); ?>" required>
                            </div>
                            <div class="form-outline form-white mb-4">
                                <label for="street" class="form-label mt-4">Street <b class="text-danger">*</b></label>
                                <input type="text" class="form-control" id="street" aria-describedby="street" name="street" value="<?php echo set_value('street'); ?>" required>
                                <span class="text-danger"><?php echo form_error('street'); ?></span>
                            </div>
                            <div class="form-outline form-white mb-4">
                                <label for="postcode" class="form-label mt-4">Post code <b class="text-danger">*</b></label>
                                <input type="text" class="form-control" id="postcode" aria-describedby="postcode" name="postcode" value="<?php echo set_value('postcode'); ?>" required>
                                <span class="text-danger"><?php echo form_error('postcode'); ?></span>
                            </div>
                            <div class="form-outline form-white mb-4">
                                <label for="streetNumber" class="form-label mt-4">Street number <b class="text-danger">*</b></label>
                                <input type="number" min="0" class="form-control" id="streetNumber" aria-describedby="streetNumber" name="streetNumber" value="<?php echo set_value('streetNumber'); ?>" required>
                                <span class="text-danger"><?php echo form_error('streetNumber'); ?></span>
                            </div>
                        </div>

                        <button class="btn btn-outline-light btn-lg px-5" type="submit" value="<?php echo $id ?>" name="submit">Create</button>
                        <?php form_close(); ?>
                    </div>
                </div>
            </div>
        </div>
    </div>
</section>