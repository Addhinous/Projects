<?php
class Conference extends CI_Controller
{
    public function __construct()
    {

        parent::__construct();
        $this->load->helper(array('form', 'url'));
        $this->load->library(['form_validation']);
        $this->load->library('session');
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

    public function edit()
    {
        if (!isset($_SESSION["id"])) {
            redirect("/");
        }
        if (!isset($this->input->get()["id"]) && !isset($_POST["submit"])) {
            redirect('/');
        }
        $id = isset($_POST["submit"]) ? intval($_POST["submit"]) : intval($this->input->get()["id"]);

        if (!$this->conference_model->get_conference_by_userId_and_conferenceId($_SESSION["id"], $id) && $_SESSION["admin"] == false) {
            redirect('/');
        }

        $data["conference"] = $this->conference_model->get_conference_by_id($id);
        $this->load->model('GenreModel');
        $this->load->model('CountryModel');
        $data["genres"] = $this->GenreModel->get_all_genres();
        $data["countries"] = $this->CountryModel->get_all_countries();
        $data["id"] = $id;

        $this->form_validation->set_rules('name', 'Name', 'required');
        $this->form_validation->set_rules('country_id', 'Country', 'required');
        $this->form_validation->set_rules('genre_id', 'Genre', 'required');
        $this->form_validation->set_rules('place', 'Place', 'required');
        $this->form_validation->set_rules('price', 'Price', 'required');
        $this->form_validation->set_rules('from', 'From', 'required');
        $this->form_validation->set_rules('to', 'Until', 'required');
        $this->form_validation->set_rules('capacity', 'Capacity', 'required');

        if ($this->form_validation->run() == false) {
            $this->load->view('templates/header');
            $this->load->view('pages/ConferenceEditView', $data);
            $this->load->view('templates/footer');
        } else {
            $sdata = [];

            if ($_FILES["image"]["size"] != 0) {
                $config['upload_path'] = './uploads/'; // upload image
                $config['allowed_types'] = 'gif|jpg|png';
                $config['max_size'] = 50000;
                $config['encrypt_name'] = true;
                $this->load->library('upload', $config);

                if ($this->upload->do_upload('image')) {
                    $sdata['image'] = $this->upload->data()["file_name"];
                }
            }

            $sdata['name'] = $this->input->post('name');
            $data['country_id'] = $this->input->post('country_id');
            $sdata['genre_id'] = $this->input->post('genre_id');
            $sdata['description'] = $this->input->post('description');
            $sdata['place'] = $this->input->post('place');
            $sdata['from'] = $this->input->post('from');
            $sdata['to'] = $this->input->post('to');
            $sdata['price'] = $this->input->post('price');
            $sdata['capacity'] = $this->input->post('capacity');
            $sdata['user_id'] = $data["conference"]["user_id"];

            if (strtotime($sdata["from"]) > strtotime($sdata["to"])) {
                $this->session->set_flashdata('date_error', 'Conference start after it ends.', 300);
                $this->load->view('templates/header');
                $this->load->view('pages/ConferenceEditView', $data);
                $this->load->view('templates/footer');
                return;
            }
            $this->load->model('Conference_model');
            if ((int)$this->Conference_model->get_count_of_tickets_on_conference($id)["count"] > (int)$sdata['capacity']) {
                $this->session->set_flashdata('capacity_error', 'Capacity is lower then count of tickets.', 300);
                $this->load->view('templates/header');
                $this->load->view('pages/ConferenceEditView', $data);
                $this->load->view('templates/footer');
                return;
            }

            $this->Conference_model->update_conference($sdata, $data["conference"]["id"]);
            redirect('conference?id=' . $id);
        }
    }

    public function create()
    {
        if (!$this->session->has_userdata("id")) {
            redirect('/');
        }

        $this->load->model('Conference_model');
        $this->load->model('GenreModel');
        $data["genres"] = $this->GenreModel->get_all_genres();
        $data["countries"] = $this->Conference_model->get_all_countries();

        $this->form_validation->set_rules('name', 'Name', 'required');
        $this->form_validation->set_rules('genre_id', 'Genre id', 'required');
        $this->form_validation->set_rules('place', 'Place', 'required');
        $this->form_validation->set_rules('country_id', 'Counry', 'required');
        $this->form_validation->set_rules('price', 'Price', 'required');
        $this->form_validation->set_rules('from', 'From', 'required');
        $this->form_validation->set_rules('to', 'Until', 'required');
        $this->form_validation->set_rules('capacity', 'Capacity', 'required');

        if ($this->form_validation->run() == false) {
            $this->load->view('templates/header');
            $this->load->view('pages/ConferenceCreateView', $data);
        } else {
            $sdata = [];
            if ($_FILES["image"]["size"] != 0) {
                $config['upload_path'] = './uploads/'; // upload image
                $config['allowed_types'] = 'gif|jpg|png';
                $config['max_size'] = 50000;
                $config['encrypt_name'] = true;
                $this->load->library('upload', $config);

                if ($this->upload->do_upload('image')) {
                    $sdata['image'] = $this->upload->data()["file_name"];
                }
            }

            $sdata['name'] = $this->input->post('name');
            $sdata['genre_id'] = $this->input->post('genre_id');
            $sdata['description'] = $this->input->post('description');
            $sdata['place'] = $this->input->post('place');
            $sdata['country_id'] = $this->input->post('country_id');
            $sdata['from'] = $this->input->post('from');
            $sdata['to'] = $this->input->post('to');
            $sdata['price'] = $this->input->post('price');
            $sdata['capacity'] = $this->input->post('capacity');
            $sdata['user_id'] = $_SESSION["id"];

            if (strtotime($sdata["from"]) > strtotime($sdata["to"])) {
                $this->session->set_flashdata('date_error', 'Conference start after it ends.', 300);
                $this->load->view('templates/header');
                $this->load->view('pages/ConferenceCreateView', $data);
                $this->load->view('templates/footer');
                return;
            }

            $this->Conference_model->insert_conference($sdata);
            $confId = $this->conference_model->get_conference_by_highest_id();
            redirect('conference?id=' . $confId["id"]);
        }

        $this->load->view('templates/footer');
    }

    public function conference()
    {
        $id = 0;
        if (isset($this->input->get()["id"]) && $this->input->get()["id"] != "" && is_numeric($this->input->get()["id"])) {
            $id = intval($this->input->get()["id"]);
        } else {
            redirect("/");
        }

        $data["conference"] = $this->conference_model->get_conference_by_id($id);
        if (!$data["conference"]) {
            redirect("/");
        }

        $this->load->model('GenreModel');
        $data["genre"] = $this->GenreModel->get_genre_by_id($data["conference"]["genre_id"]);

        $this->load->model('PresentationModel');
        $data["presentations"] = $this->PresentationModel->get_presentations_by_conference_id($id);

        $result = $this->conference_model->get_sold_tickets_count_by_conference_id($id);
        $data["available"] = $data["conference"]["capacity"] - $result["sold"];

        $this->load->view('templates/header');
        $this->load->view('pages/ConferenceDetailView', $data);
        $this->load->view('templates/footer');
    }

    public function removeConference()
    {
        $this->conference_model->delete_conference_by_id($this->input->post('removed'));
        redirect("user/user");
    }
}
