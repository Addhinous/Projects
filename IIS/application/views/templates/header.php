<!doctype html>
<html>

<head>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Conference Book</title>
  <link rel="stylesheet" href="https://bootswatch.com/5/darkly/bootstrap.min.css">
  <link rel="stylesheet" type="text/css" href="<?php echo base_url(); ?>css/style.css">
  <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>
  <script type='text/javascript' src="<?php echo base_url(); ?>js/main.js"></script>
  <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css" integrity="sha384-wvfXpqpZZVQGK6TAh5PVlGOfQNHSoD2xbE+QkPxCAFlNEevoEH3Sl0sibVcOQVnN" crossorigin="anonymous">
  <script>
    loggedIn = <?php echo isset($_SESSION["id"]) ? "1" : "0" ?>
  </script>
  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-ka7Sk0Gln4gmtz2MlQnikT1wXgYsOg+OMhuP+IlRH9sENBO0LRn5q+8nbTov4+1p" crossorigin="anonymous"></script>
</head>

<body>
  <nav class="navbar navbar-expand-lg navbar-dark bg-primary fixed-top">
    <div class="container-fluid">
      <a class="navbar-brand" href=<?php echo base_url(); ?>><b style="color: orange; text-shadow: -1px 0 black, 0 1px black, 1px 0 black, 0 -1px black;">Conference</b><span style="color: #fff; text-shadow: -1px 0 black, 0 1px black, 1px 0 black, 0 -1px black;">Book</span></a>
      <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarColor01" aria-controls="navbarColor01" aria-expanded="false" aria-label="Toggle navigation">
        <span class="navbar-toggler-icon"></span>
      </button>

      <div class="collapse navbar-collapse" id="navbarColor01">
        <ul class="navbar-nav me-auto">
          <li class="nav-item">
            <a class="nav-link" href=<?php echo base_url(); ?>>Conferences</a>
          </li>
          <li class="nav-item">
            <a class="nav-link" href=<?php echo site_url('contacts'); ?>>Contacts</a>
          </li>
        </ul>
        <?php if ($this->session->has_userdata('email')) : ?>
          <ul class="nav navbar-nav navbar-right">
            <li class="nav-item dropdown dropleft">
              <a class="nav-link dropdown-toggle" data-bs-toggle="dropdown" role="button" aria-haspopup="true" aria-expanded="false">My account</a>
              <div class="dropdown-menu neco" style="left: -50px">
                <a class="dropdown-item" href=<?php echo site_url('user/user'); ?>>my account</a>
                <div class="dropdown-divider"></div>
                <a class="dropdown-item" href=<?php echo site_url('userAccessController/logout'); ?>>Logout</a>
              </div>
            </li>
          </ul>
        <?php else : ?>
          <ul class="navbar-nav navbar-right">
            <li class="nav-item">
              <a class="nav-link" href=<?php echo site_url('userAccessController/login'); ?>>Login</a>
            </li>
            <li class="nav-item">
              <a class="nav-link" href=<?php echo site_url('userAccessController/registration'); ?>>Sign up</a>
            </li>
          </ul>
        <?php endif; ?>
      </div>
    </div>
  </nav>
  <div style="margin-top:72px"></div>