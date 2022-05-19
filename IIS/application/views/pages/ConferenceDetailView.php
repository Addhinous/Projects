<div class="detail-img">
  <div class="card">
    <div class="card-body">
      <h3 class="card-title"><?php echo $conference["name"] ?></h3>
      <br>
      <div>
        <div class="white-box text-center">

          <?php if ($conference["image"] == "") : ?>
            <svg xmlns="http://www.w3.org/2000/svg" class="d-block user-select-none" width="100%" height="200" aria-label="Placeholder: Image cap" focusable="false" role="img" preserveAspectRatio="xMidYMid slice" viewBox="0 0 318 180" style="font-size:1.125rem;text-anchor:middle">
              <rect width="100%" height="100%" fill="#868e96"></rect>
              <text x="50%" y="50%" fill="#dee2e6" dy=".3em">Imageless</text>
            </svg>
          <?php else : ?>
            <img src="<?php echo "uploads/" . $conference["image"] ?>" class="responsive-img">
          <?php endif; ?>
        </div>
      </div>
      <br>
    </div>
    </div>
    <?php if((isset($_SESSION['id']) && ($_SESSION['id'] == $conference["user_id"])) || (isset($_SESSION['admin']) && intval($_SESSION['admin']))):?>
    <a href=<?php echo '"' . base_url() . 'conferenceedit?id=' . $conference["id"] . '"' ?>>
      <button type="button" class="btn btn-labeled btn-outline-info mt-3 ms-2">
          <span class="btn-label"></span>Edit conference
      </button>
    </a>
    <a href=<?php echo site_url('managerTimePlanner?id=').$conference["id"]; ?>>
      <button type="button" class="btn btn-labeled btn-outline-info mt-3 ms-2">
          <span class="btn-label"></span>Manage my conference
      </button>
    </a>
    <?php endif;?>
</div>

<div class="detail-desc">
  <ul class="nav nav-tabs">
    <li class="nav-item">
      <a class="nav-link active" data-bs-toggle="tab" href="#info">Info</a>
    </li>
    <li class="nav-item">
      <a class="nav-link" data-bs-toggle="tab" href="#presentations">Presentations</a>
    </li>
  </ul>
  <div id="myTabContent" class="tab-content">
    <div class="tab-pane fade show active" id="info" style="margin-top: 5%">
      <h3>Location</h3>
      <?php echo $conference["place"] ?><br></br>
      <h3>Date and time</h3>
      From <?php echo date("d. m. Y H:i", strtotime($conference["from"])) ?> <br>Until <?php echo date("d. m. Y H:i", strtotime($conference["to"])) ?><br></br>
      <h3>Genre</h3>
      <?php echo $genre["name"] ?><br></br>
      <h3>Description</h3>
      <p><?php echo $conference["description"];?></p>
      <div style="float:left">
        <h3>Free slots</h3>
        <p><?php echo $available . "/" . $conference["capacity"] ?></p>
      </div>
      <div style="float:left; margin-left: 50px">
        <h3>Price</h3>
        <p><?php echo $conference["price"] ?> $ / ticket</p>
      </div>

      <div style="margin-left: 50px; margin-top: 20px;float:left; margin-bottom: 10px">
        <form action="<?php echo site_url('reserveTickets'); ?>" method="get">
          <input type="hidden" name="reserve" value="<?= $conference["id"] ?>">
          <button type="submit" class="btn btn-primary">Reserve tickets</button>
        </form>
        
      </div>
    </div>
    <div class="tab-pane fade" id="presentations" style="margin-top: 20px; margin-bottom: 20px">
      <div class="accordion" id="accordion1">
        <?php $num = 1;?>
        <?php foreach ($presentations as $presentation) : ?>
          <?php if($presentation["confirmed"]):?>
          <?php $heading = "heading".$num; $num++; $unique_id = "collapse".$num?>
          <div class="accordion-item">
            <h2 class="accordion-header" id="<?php echo $heading; ?>">
              <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#<?php echo $unique_id; ?>" aria-expanded="false" aria-controls="<?php echo $unique_id; ?>">
                <?php echo $presentation["name"] ?> <?php echo date("H:i", strtotime($presentation["start"])) ?> - <?php echo date("H:i", strtotime($presentation["finish"])) ?>
              </button>
            </h2>
            <div id="<?php echo $unique_id; ?>" class="accordion-collapse collapse" aria-labelledby="<?php echo $heading; ?>" data-bs-parent="#accordion1">
              <div class="accordion-body">
                <strong> <?php echo $presentation["tags"] ?></strong> <br></br>
                <a href=<?php echo '"' . base_url() . 'presentation?id=' . $presentation["id"] . '"' ?> class="card-link">View details</a>
              </div>
            </div>
          </div>
        <?php endif; ?>
        <?php endforeach; ?>
      </div>
      <?php if(isset($_SESSION["id"])):?>
      <form action=<?php echo site_url('PresentationCreate')?> method="get">
          <input type="hidden" value="<?= $conference["id"] ?>" name="conference_id">
          <button type="submit" class="btn btn-labeled btn-outline-info mt-3 ms-2">
              <span class="btn-label"></span>Create a presentation
          </button>
      </form>
      <?php endif; ?>
    </div>
  </div>
</div>