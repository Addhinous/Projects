<script type='text/javascript' src="<?php echo base_url(); ?>js/user.js"></script>
<script>
    ajaxPath = "<?php echo base_url() ?>"
</script>
<link rel="stylesheet" type="text/css" href="<?php echo base_url(); ?>css/user.css">
<div style="margin-top: 80px"></div>
<div class="alert alert-dismissible alert-success" id="alertChangedUserInforamtions" style="display: none">
    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    <strong>successfully changed your informations</strong>.
</div>
<button type="button" class="btn btn-labeled btn-outline-info mt-3 ms-2" data-bs-toggle="modal" onclick="editMeModal()" data-bs-target="#userEditMeModal">
    <span class="btn-label"><i class="fa fa-cogs me-1 "></i></span>Edit my account</button>
<div>
    <ul class="nav nav-tabs mt-5">
        <li class="nav-item">
            <a class="nav-link active" data-bs-toggle="tab" href="#mytickets">My Tickets</a>
        </li>
        <li class="nav-item">
            <a class="nav-link" data-bs-toggle="tab" href="#mypresentations">My Presentations</a>
        </li>
        <li class="nav-item">
            <a class="nav-link" data-bs-toggle="tab" href="#myconferences">My Conferences</a>
        </li>
    </ul>
    <div id="tabUserDeatail" class="tab-content">
        <div class="tab-pane fade active show tableDivContainer" id="mytickets">
            <?php if (count($tickets) > 0) : ?>
                <table class="table table-hover">
                    <thead>
                        <tr>
                            <th scope="col">Conference</th>
                            <th scope="col">Ticket count</th>
                            <th scope="col">Code</th>
                            <th scope="col">Date</th>
                            <th scope="col">Paid</th>
                            <th scope="col"></th>
                        </tr>
                    </thead>
                    <tbody>
                        <?php foreach ($tickets as $ticket) : ?>
                            <tr>
                                <th scope="row"><a href=<?php echo '"' . base_url() . 'conference?id=' . $ticket["id"] . '"' ?>><?php echo $ticket["name"] ?></a></th>
                                <td><?php echo $ticket["count"] ?></td>
                                <td><?php echo $ticket["code"] ?></td>
                                <td><?php echo $ticket["from"] . " - " . $ticket["to"] ?></td>
                                <td><?php echo intval($ticket["paid"]) ? '<i class="text-success fa fa-check me-1 "></i>' : '<i class="text-danger fa fa-close me-1 "></i>' ?></td>

                                </td>
                                <td>
                                    <form onsubmit="return confirm('Do you really want to delete your reservation ?')" method="post" action="<?php echo base_url() . 'removeTicket' ?>">
                                        <input type="hidden" name="removed" value="<?php echo $ticket["code"] ?>">
                                        <button type="submit" class="btn btn-danger">Cancel</button>
                                    </form>
                                </td>
                            </tr>
                        <?php endforeach; ?>
                    </tbody>
                </table>
            <?php else : ?>
                <h6 class="ms-2 mt-1">You have no tickets</h6>
            <?php endif; ?>
        </div>
        <div class="tab-pane fade" id="mypresentations">
            <?php if (count($presentations) > 0) : ?>
                <table class="table table-hover">
                    <thead>
                        <tr>
                            <th scope="col">Presentation</th>
                            <th scope="col">Conference</th>
                            <th scope="col">Date</th>
                            <th scope="col">Confirmed</th>
                        </tr>
                    </thead>
                    <tbody>
                        <?php foreach ($presentations as $pres) : ?>
                            <tr>
                                <th scope="row"><a href=<?php echo '"' . base_url() . 'presentation?id=' . $pres["id"] . '"' ?>><?php echo $pres["p_name"] ?></a></th>
                                <td><a href=<?php echo '"' . base_url() . 'conference?id=' . $pres["conference_id"] . '"' ?>><?php echo $pres["c_name"] ?></a></td>
                                <td><?php echo $pres["start"] . " - " . $pres["finish"] ?></td>
                                <td><?php echo intval($pres["confirmed"]) ? '<i class="text-success fa fa-check me-1 "></i>' : '<i class="text-danger fa fa-close me-1 "></i>' ?></td>
                                <td>
                                    <form onsubmit="return confirm('Do you really want to delete your presentation ?')" method="post" action="<?php echo base_url() . 'removePresentation' ?>">
                                        <input type="hidden" name="removed" value="<?php echo $pres["id"] ?>">
                                        <button type="submit" class="btn btn-danger">Cancel</button>
                                    </form>
                                </td>
                            </tr>
                        <?php endforeach; ?>
                    </tbody>
                </table>
            <?php else : ?>
                <h6 class="ms-2 mt-1">You have no presentations</h6>
            <?php endif; ?>
        </div>
        <div class="tab-pane fade" id="myconferences">
            <?php if (count($conferences) > 0) : ?>
                <table class="table table-hover">
                    <thead>
                        <tr>
                            <th scope="col">Conference</th>
                            <th scope="col">Tickets reserved</th>
                            <th scope="col">Date</th>
                        </tr>
                    </thead>
                    <tbody>

                        <?php foreach ($conferences as $conf) : ?>
                            <tr>
                                <th scope="row"><a href=<?php echo '"' . base_url() . 'conference?id=' . $conf["id"] . '"' ?>><?php echo $conf["name"] ?></a></th>
                                <td><?php echo $conf["reserved"] . "/" . $conf["capacity"] ?></td>
                                <td><?php echo $conf["from"] . " - " . $conf["to"] ?></td>
                                <td>
                                    <form onsubmit="return confirm('Do you really want to delete your conference ?')" method="post" action="<?php echo base_url() . 'removeConference' ?>">
                                        <input type="hidden" name="removed" value="<?php echo $conf["id"] ?>">
                                        <button type="submit" class="btn btn-danger">Cancel</button>
                                    </form>
                                </td>
                            </tr>
                        <?php endforeach; ?>

                    </tbody>
                </table>
            <?php else : ?>
                <h6 class="ms-2 mt-1">You have no conferences</h6>
            <?php endif; ?>
            <a href=<?php echo site_url('conferencecreate'); ?>>
                <button type="button" class="btn btn-labeled btn-outline-info mt-3 ms-2">
                    <span class="btn-label"></span>Create a conference
                </button>
            </a>
        </div>
    </div>
</div>
<br>
<?php if (isset($users)) : ?>
    <h3 class="ms-2">Users</h3>
    <div class="form-group ms-2">
        <input class="form-control" id="usersFilter" placeholder="Search">
    </div>
    <br>
    <div class="tableDivContainer mb-5">
        <table class="table table-hover">
            <thead>
                <tr>
                    <th scope="col">Email</th>
                    <th scope="col">Name</th>
                    <th scope="col">Surename</th>
                    <th scope="col">Conferences</th>
                    <th scope="col">Presentations</th>
                    <th scope="col">Action</th>
                </tr>
            </thead>
            <tbody id="usersTbody">
                <?php foreach ($users as $user) : ?>
                    <tr>
                        <th scope="row" <?php echo intval($user["is_deactivated"]) ? 'style="color: red"' : "" ?>><?php echo $user["email"] . (intval($user["is_admin"]) ? ' <span style="color: #00ffb8" >(admin)</span>' : "") ?></th>
                        <td><?php echo $user["name"]  ?></td>
                        <td><?php echo $user["surename"] ?></td>
                        <td <?php if (!intval($user["conferences"])) {
                                echo 'style="color: grey"';
                            } ?>> <?php echo $user["conferences"] ?></td>
                        <td <?php if (!intval($user["presentations"])) {
                                echo 'style="color: grey"';
                            } ?>> <?php echo $user["presentations"] ?></td>
                        <td>
                            <a href="" data-bs-toggle="modal" onclick=<?php echo '"editUserModal(' . $user["id"] . ')"' ?> data-bs-target="#userEditModal">Edit</a>
                        </td>
                    </tr>
                <?php endforeach; ?>
            </tbody>
        </table>
    </div>
    <div class="modal fade" id="userEditModal" tabindex="-1" aria-labelledby="userEditModalLabel" aria-hidden="true">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="userEditModalLabel">Edit user</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <fieldset>
                        <div class="form-group">
                            <label for="modalInputEmail" class="form-label mt-4">Email address</label>
                            <input type="email" class="form-control" id="modalInputEmail" aria-describedby="emailHelp" placeholder="Enter email">
                            <div class="invalid-feedback">User with this email already exist or wrong format of email</div>
                        </div>
                        <div class="form-group">
                            <label for="modalInputName" class="form-label mt-4">Name</label>
                            <input type="email" class="form-control" id="modalInputName" aria-describedby="emailHelp" placeholder="Enter name">
                        </div>
                        <div class="form-group">
                            <label for="modalInputSurename" class="form-label mt-4">Surename</label>
                            <input type="email" class="form-control" id="modalInputSurename" aria-describedby="emailHelp" placeholder="Enter surename">
                        </div>
                        <br>
                        <div class="form-check">
                            <input class="form-check-input" type="checkbox" value="" id="modalCheckboxAdmin">
                            <label class="form-check-label" for="modalCheckboxAdmin">
                                Admin
                            </label>
                        </div>
                        <br>
                        <div class="form-check">
                            <input class="form-check-input" type="checkbox" value="" id="modalCheckboxDeactivated">
                            <label class="form-check-label" for="modalCheckboxDeactivated">
                                Deactivated
                            </label>
                        </div>
                        <br>
                        <button class="btn btn-primary" id="editSubmit" onclick="editUserModalSubmit()">Edit</button>
                        <button class="btn btn-danger float-end" data-bs-dismiss="modal" onclick="deleteUserModalSubmit()">Delete user</button>
                    </fieldset>
                </div>
            </div>
        </div>
    </div>
<?php endif; ?>
<div class="modal fade" id="userEditMeModal" tabindex="-1" aria-labelledby="userEditMeModalLabel" aria-hidden="true">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title" id="userEditMeModalLabel">Edit My informations</h5>
                <button type="button" class="btn-close" id="userEditMeModalCloseBtn" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
                <fieldset>
                    <div class="form-group">
                        <label for="modalInputMyEmail" class="form-label mt-4">Email address</label>
                        <input type="email" class="form-control" id="modalInputMyEmail" aria-describedby="emailHelp" placeholder="Enter email">
                        <div class="invalid-feedback">User with this email already exist or wrong format of email</div>
                    </div>
                    <div class="form-group">
                        <label for="modalInputMyName" class="form-label mt-4">Name</label>
                        <input type="email" class="form-control" id="modalInputMyName" aria-describedby="emailHelp" placeholder="Enter name">
                    </div>
                    <div class="form-group">
                        <label for="modalInputMySurename" class="form-label mt-4">Surename</label>
                        <input type="email" class="form-control" id="modalInputMySurename" aria-describedby="emailHelp" placeholder="Enter surename">
                    </div>
                    <br>
                    <div class="form-check">
                        <input class="form-check-input" type="checkbox" value="" id="modalChangePassword">
                        <label class="form-check-label" for="modalChangePassword">
                            Change password
                        </label>
                    </div>
                    <div class="ms-3">
                        <div class="form-group">
                            <label for="modalMyOldPassword" class="form-label mt-4">Old Password</label>
                            <input type="password" class="form-control" id="modalMyOldPassword" aria-describedby="emailHelp" placeholder="Enter old password" disabled>
                            <div class="invalid-feedback">Wrong password</div>
                        </div>
                        <div class="form-group">
                            <label for="modalMyNewPassword" class="form-label mt-4">New Password</label>
                            <input type="password" class="form-control" id="modalMyNewPassword" aria-describedby="emailHelp" placeholder="Enter new password" disabled>
                            <div class="invalid-feedback">Passwords must be 6 characters long and contain at leats 1 number, 1 Big char and 1 small cahr</div>
                        </div>
                        <div class="form-group">
                            <label for="modalMyNewPasswordAgain" class="form-label mt-4">New Password Again</label>
                            <input type="password" class="form-control" id="modalMyNewPasswordAgain" aria-describedby="emailHelp" placeholder="Enter new passrod again" disabled>
                            <div class="invalid-feedback">Passwords are not same</div>
                        </div>
                    </div>
                    <br>
                    <button class="btn btn-primary" id="editMeSubmit" onclick="editUserMeModalSubmit()">Edit</button>
                </fieldset>
            </div>
        </div>
    </div>
</div>