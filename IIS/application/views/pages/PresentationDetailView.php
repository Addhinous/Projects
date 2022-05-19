<div class="detail-img" style="margin-left: 10px; margin-right: 10px;">
  <div class="card">
    <div class="card-body">
      <h3 class="card-title"><?php echo $presentation["name"] ?></h3>
      <br>
      <div>
        <div class="white-box text-center">

          <?php if ($presentation["image"] == "") : ?>
            <svg xmlns="http://www.w3.org/2000/svg" class="d-block user-select-none" width="100%" height="200" aria-label="Placeholder: Image cap" focusable="false" role="img" preserveAspectRatio="xMidYMid slice" viewBox="0 0 318 180" style="font-size:1.125rem;text-anchor:middle">
              <rect width="100%" height="100%" fill="#868e96"></rect>
              <text x="50%" y="50%" fill="#dee2e6" dy=".3em">Imageless</text>
            </svg>
          <?php else : ?>
            <img src="<?php echo "uploads/" . $presentation["image"] ?>" class="responsive-img">
          <?php endif; ?>
          
        </div>
      </div>
      <h3 style="margin-top: 10px">Lecturer:</h3>
      <?php echo $user->name . " " . $user->surename ?>
      <br>
    </div>
  </div>
  <?php if((isset($_SESSION['id']) && ($_SESSION['id'] == $presentation["user_id"])) || (isset($_SESSION['admin']) && intval($_SESSION['admin']))):?>
    <a href=<?php echo '"' . base_url() . 'PresentationEdit?id=' . $presentation["id"] . '"' ?>>
      <button type="button" class="btn btn-labeled btn-outline-info mt-3 ms-2">
          <span class="btn-label"></span>Edit presentation
      </button>
    </a>
  <?php endif;?><br></br>
  <a href=<?php echo '"' . base_url() . 'conference?id=' . $presentation["conference_id"] . '"' ?> class="card-link" style="margin-left: 10px">Back to conference</a>
</div>


<div style="margin-top: 80px; margin-left: 10px">
  <?php if(isset($presentation["start"]) && isset($presentation["finish"]) && isset($presentation["room_id"])): ?>
    <h3>Location</h3>
    Room <?php echo $room["name"];?><br></br>
    <?php echo $room["city"] . ", " . $room["street"] . " " . $room["street_number"] . ", " . $room["postcode"]?><br></br>
    <h3>Date and time</h3>
    From <?php echo date("d. m. Y H:i", strtotime($presentation["start"])) ?> <br>Until <?php echo date("d. m. Y H:i", strtotime($presentation["finish"])) ?><br></br>
  <?php endif; ?>  
    <h3>Description</h3>
    <p><?php echo $presentation["description"] ?></p>
    <?php echo $presentation["tags"] ?><br></br>
</div>
