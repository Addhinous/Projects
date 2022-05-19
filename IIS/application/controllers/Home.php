<?php
class Home extends CI_Controller
{
    public function __construct()
    {
        parent::__construct();
        $this->load->helper(array('form', 'url'));
        $this->load->library(['form_validation', 'session']);
        $this->load->database();
        $this->autoLogout();
    }

    private function autoLogout()
    {
        if (isset($_SESSION["id"])) {
            if ((time() - $_SESSION['last_login_timestamp']) > 600) {
                $this->session->sess_destroy();
                redirect('/', 'refresh');
            } else {
                $_SESSION["last_login_timestamp"] = time();
            }
        }
    }

    public function home()
    {
        if (!file_exists(APPPATH . 'views/pages/home.php')) {
            show_404();
        }

        $data["conferences"] = $this->conference_model->get_all_conferences();
        $this->load->model('GenreModel');
        $data["genres"] = $this->GenreModel->get_all_genres();
        $this->load->model('CountryModel');
        $data["countries"] = $this->CountryModel->get_all_countries();

        foreach ($data["conferences"] as $key => $value) {
            $data["conferences"][$key]["country"] = $this->CountryModel->get_country_by_id($value["country_id"]);
        }
        foreach ($data["conferences"] as $key => $value) {
            $data["conferences"][$key]["genre"] = $this->GenreModel->get_genre_by_id($value["genre_id"]);
        }
        foreach ($data["conferences"] as $key => $value) {
            $data["conferences"][$key]["left"] = $value["capacity"] - $this->conference_model->get_sold_tickets_count_by_conference_id($value["id"])["sold"];
        }

        $data["justloggedin"] = $this->session->has_userdata('justloggedin');
        $this->session->unset_userdata('justloggedin');

        $this->load->view('templates/header');
        $this->load->view('pages/home', $data);
        $this->load->view('templates/footer');
    }

    public function contacts()
    {
        $this->load->view('templates/header');
        $this->load->view('pages/contacts');
        $this->load->view('templates/footer');
    }
}
