<link rel="stylesheet" type="text/css" href="<?php echo base_url(); ?>css/manager.css">
<script type='text/javascript' src="<?php echo base_url(); ?>js/manager.js"></script>
<script>
    ajaxPath = "<?php echo base_url() ?>"
</script>
<button type="button" class="btn btn-labeled btn-outline-info mt-3 ms-2" data-bs-toggle="modal" data-bs-target="#addRoomModal"><span class="btn-label">
        <i class="fa fa-list me-1 "></i></span>Rooms</button>

<button type="button" class="btn btn-labeled btn-outline-info mt-3 ms-2" data-bs-toggle="modal" data-bs-target="#presentationModal"><span class="btn-label">
        <i class="fa fa-list me-1 "></i></span>Presentations</button>

<button type="button" class="btn btn-labeled btn-outline-info mt-3 ms-2" data-bs-toggle="modal" data-bs-target="#reservationModal"><span class="btn-label">
        <i class="fa fa-list me-1 "></i></span>Reservations</button>

<br>
<form method="post" class="ms-2">
    <fieldset>
        <div class="form-group d-inline-block">
            <label for="selectPresentation" class="form-label mt-4">Presentation</label>
            <select class="form-select" id="selectPresentation" name="selectPresentation">
                <?php foreach ($presentations as $presentation) : ?>
                    <option value="<?php echo $presentation["id"] ?>" <?php echo $presentation["id"] == set_value('selectPresentation') ? "selected" : ""; ?>><?php echo $presentation["name"] ?></option>
                <?php endforeach; ?>
            </select>
            <?php echo form_error('selectPresentation'); ?>
        </div>
        <div class="form-group d-inline-block">
            <label for="selectRoom" class="form-label mt-4">Room</label>
            <select class="form-select" id="selectRoom" name="selectRoom">
                <?php foreach ($rooms as $room) : ?>
                    <option value="<?php echo $room["id"] ?>" <?php echo $room["id"] == set_value('selectRoom') ? "selected" : ""; ?>><?php echo $room["name"] ?></option>
                <?php endforeach; ?>
            </select>
            <?php echo form_error('selectRoom'); ?>
        </div>
        <div class="form-group d-inline-block">
            <label for="inputDateFrom" class="form-label mt-4">From</label>
            <input type="datetime-local" class="form-control" id="inputDateFrom" placeholder="Enter date from" name="inputDateFrom" value="<?php echo set_value('inputDateFrom'); ?>">
            <span class="text-danger"><?php echo form_error('inputDateFrom'); ?></span>
        </div>
        <div class="form-group d-inline-block">
            <label for="inputDateTo" class="form-label mt-4">To</label>
            <input type="datetime-local" class="form-control" id="inputDateTo" placeholder="Enter date until" name="inputDateTo" value="<?php echo set_value('inputDateTo'); ?>">
            <span class="text-danger"><?php echo form_error('inputDateTo'); ?></span>
        </div>
        <button type="submit" class="btn btn-primary d-inline-block" style="margin-top:-4px">Confirm</button>
    </fieldset>
    <p class="text-danger"><?php echo $this->session->flashdata("date_error");
                            echo $this->session->flashdata("presentation_error");
                            echo $this->session->flashdata("room_error");
                            echo $this->session->flashdata("conf_date_error"); ?></p>
    <?php unset($_SESSION["room_error"], $_SESSION["presentation_error"], $_SESSION["date_error"], $_SESSION["conf_date_error"]); ?>
</form>
<br>
<table class="table table-hover">
    <thead>
        <tr>
            <th scope="col">Room</th>
            <th scope="col">Presentation</th>
            <th scope="col">Start</th>
            <th scope="col">End</th>
            <th scope="col"></th>
        </tr>
    </thead>
    <tbody>
        <?php foreach ($plan as $item) : ?>
            <tr>
                <td><?php echo $item["rname"] ?></td>
                <td><a href=<?php echo '"' . base_url() . 'presentation?id=' . $presentation["id"] . '"' ?>><?php echo $item["name"] ?></a></td>
                <td><?php echo $item["start"] ?></td>
                <td><?php echo $item["finish"] ?></td>
                <td><button class="btn btn-danger" onclick="removePlanItem(this, <?php echo $item['id'] ?>)">Remove</button></td>
            </tr>
        <?php endforeach; ?>
    </tbody>
</table>

<div class="modal fade" id="addRoomModal" tabindex="-1" aria-labelledby="addRoomModalLabel" aria-hidden="true">
    <div class="modal-dialog modal-xl">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title" id="addRoomModalLabel">Rooms</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>

            <div class="form-group ms-2">
                <input class="form-control w-auto mt-1" id="roomsFilter" placeholder="Search">
            </div>

            <div class="modal-body">
                <table class="table table-hover">
                    <thead>
                        <tr>
                            <th scope="col">Name</th>
                            <th scope="col">City</th>
                            <th scope="col">Street</th>
                            <th scope="col">Street number</th>
                            <th scope="col">Postcoce</th>
                            <th scope="col"></th>
                        </tr>
                    </thead>
                    <tbody id="roomsTbody">
                        <?php foreach ($rooms as $room) : ?>
                            <tr>
                                <td><?php echo $room["name"] ?></td>
                                <td><?php echo $room["city"] ?></td>
                                <td><?php echo $room["street"] ?></td>
                                <td><?php echo $room["street_number"] ?></td>
                                <td><?php echo $room["postcode"] ?></td>
                                <td><a href="<?php echo base_url() . 'roomedit?id=' . $room["id"] ?>"><button class="btn btn-info">Edit</button></a>
                                    <button class="btn btn-danger ms-2" onclick="deleteRoomById(this, <?php echo $room['id'] ?>)">Delete</button>
                                </td>
                            </tr>
                        <?php endforeach; ?>
                    </tbody>
                </table>
                <a href="<?php echo base_url() . 'roomcreate?id=' . $_GET['id'] ?>"><button class="btn btn-primary">Add</button></a>
            </div>
        </div>
    </div>
</div>

<div class="modal fade" id="presentationModal" tabindex="-1" aria-labelledby="presentationModalLabel" aria-hidden="true">
    <div class="modal-dialog ">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title" id="presentationModalLabel">Presentations</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="form-group ms-2">
                <input class="form-control w-auto mt-1" id="presentationsFilter" placeholder="Search">
            </div>
            <div class="modal-body">
                <?php echo form_open('conferenceManagerController/confirmPresentation', "", ["id" => $_GET["id"]]); ?>
                <table class="table table-hover">
                    <thead>
                        <tr>
                            <th scope="col">Name</th>
                            <th scope="col">Confirmed</th>
                        </tr>
                    </thead>
                    <tbody id="presentationsTbody">
                        <?php foreach ($allpresentations as $presentation) : ?>
                            <tr>
                                <td><a href=<?php echo '"' . base_url() . 'presentation?id=' . $presentation["id"] . '"' ?>><?php echo $presentation["name"] ?></a></td>
                                <td>
                                    <?php if ($presentation["confirmed"]) : ?>
                                        <input class="form-check-input" type="checkbox" value="<?php echo $presentation["id"] ?>" name="<?php echo $presentation["id"] ?>" checked style="vertical-align: middle; position: relative;">
                                    <?php else : ?>
                                        <input class="form-check-input" type="checkbox" value="<?php echo $presentation["id"] ?>" name="<?php echo $presentation["id"] ?>">
                                    <?php endif; ?>
                                </td>
                            </tr>
                        <?php endforeach; ?>
                    </tbody>
                </table>
                <button type="submit" class="btn btn-primary">Confirm</button>
                <?php echo form_close(); ?>
            </div>
        </div>
    </div>
</div>

<div class="modal fade" id="reservationModal" tabindex="-1" aria-labelledby="reservationModalLabel" aria-hidden="true">
    <div class="modal-dialog modal-xl">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title" id="reservationModalLabel">Reservations</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="form-group ms-2">
                <input class="form-control w-auto mt-1" id="reservationsFilter" placeholder="Search">
            </div>
            <div class="modal-body">
                <?php echo form_open('conferenceManagerController/confirmReservation', "", ["id" => $_GET["id"]]); ?>
                <table class="table table-hover">
                    <thead>
                        <tr>
                            <th scope="col">Name</th>
                            <th scope="col">Surename</th>
                            <th scope="col">Email</th>
                            <th scope="col">Code</th>
                            <th scope="col">Count</th>
                            <th scope="col">Created</th>
                            <th scope="col">Paid</th>
                            <th scope="col"></th>
                        </tr>
                    </thead>
                    <tbody id="reservationsTbody">
                        <?php foreach ($reservations as $reservation) : ?>
                            <tr>
                                <td><?php echo $reservation["name"] ?></td>
                                <td><?php echo $reservation["surename"] ?></td>
                                <td><?php echo $reservation["email"] ?></td>
                                <td><?php echo $reservation["code"] ?></td>
                                <td><?php echo $reservation["count"] ?></td>
                                <td><?php echo $reservation["created"] ?></td>
                                <td>
                                    <?php if ($reservation["paid"]) : ?>
                                        <input class="form-check-input" type="checkbox" value="<?php echo $reservation["code"] ?>" name="<?php echo $reservation["code"] ?>" id="flexCheckDefault" checked style="vertical-align: middle; position: relative;">
                                    <?php else : ?>
                                        <input class="form-check-input" type="checkbox" value="<?php echo $reservation["code"] ?>" name="<?php echo $reservation["code"] ?>" id="flexCheckDefault">
                                    <?php endif; ?>
                                </td>
                                <?php if (!$reservation["paid"]) : ?>
                                    <?php $jsfce = 'removeResrvationsByCode(this,"' . $reservation['code'] . '")' ?>
                                    <td><button type="button" onclick='<?php echo $jsfce ?>' class="btn btn-danger ms-2">Delete</button></td>
                                <?php endif; ?>
                            </tr>
                        <?php endforeach; ?>
                    </tbody>
                </table>
                <button type="submit" class="btn btn-primary ms-2">Confirm</button>
                <?php echo form_close(); ?>
            </div>
        </div>
    </div>
</div>