<?php
class PresentationController extends CI_Controller
{
    public function __construct()
    {
        parent::__construct();
        $this->load->helper(array('form', 'url'));
        $this->load->library(['form_validation']);
        $this->load->library('session');
        $this->load->model("PresentationModel");
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

        if (!isset($this->input->get()["id"]) && !isset($_POST["submit"])) {
            redirect('/');
        }
        $id = isset($_POST["submit"]) ? intval($_POST["submit"]) : intval($this->input->get()["id"]);

        $data["presentation"] = $this->PresentationModel->get_presentation_by_id($id);
        $this->load->model('RoomModel');
        $data["rooms"] = $this->RoomModel->get_rooms_by_conference_id($data["presentation"]["conference_id"]);
        $data["id"] = $id;

        $this->form_validation->set_rules('name', 'Name', 'required');

        if ($this->form_validation->run() == false) {
            $this->load->view('templates/header');
            $this->load->view('pages/PresentationEditView', $data);
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
            $sdata['room_id'] = $this->input->post('room_id');
            $sdata['description'] = $this->input->post('description');
            $sdata['tags'] = $this->input->post('tags');
            $sdata['user_id'] = $_SESSION["id"];

            $this->PresentationModel->update_presentation($sdata, $data["presentation"]["id"]);
            redirect('presentation?id=' . $id);
        }
    }

    public function create()
    {
        if (!isset($this->input->get()["conference_id"]) && !isset($this->input->post()["conference_id"])) {
            redirect('/');
        }

        $data["conference_id"] = isset($this->input->get()["conference_id"]) ? $this->input->get()["conference_id"] : $this->input->post()["conference_id"];

        $this->load->model('RoomModel');
        $data["rooms"] = $this->RoomModel->get_rooms_by_conference_id($data["conference_id"]);

        $this->form_validation->set_rules('name', 'Name', 'required');

        if ($this->form_validation->run() == false) {
            $this->load->view('templates/header');
            $this->load->view('pages/PresentationCreateView', $data);
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
            $sdata['room_id'] = $this->input->post('room_id');
            $sdata['description'] = $this->input->post('description');
            $sdata['tags'] = $this->input->post('tags');
            $sdata['conference_id'] = $this->input->post('conference_id');
            $sdata['user_id'] = $_SESSION["id"];

            $this->load->model('PresentationModel');
            $this->PresentationModel->insert_presentation($sdata);
            $presentation = $this->PresentationModel->get_presentation_by_highest_id();
            redirect('presentation?id=' . $presentation["id"]);
        }

        $this->load->view('templates/footer');
    }

    public function presentation()
    {

        $id = 0;

        if (isset($this->input->get()["id"])) {
            $id = intval($this->input->get()["id"]);
        } else {
            redirect("/");
        }

        $data["presentation"] = $this->PresentationModel->get_presentation_by_id($id);
        if (!$data["presentation"]) {
            redirect("/");
        }
        $this->load->model('RoomModel');
        $data["room"] = $this->RoomModel->get_room_by_id($data["presentation"]["room_id"]);

        if ($data["presentation"]["user_id"]) {
            $this->load->model('User_model');
            $data["user"] = $this->User_model->get_user_by_id($data["presentation"]["user_id"]);
        }
        $this->load->view('templates/header');
        $this->load->view('pages/PresentationDetailView', $data);
        $this->load->view('templates/footer');
    }

    public function removePresentation()
    {
        $this->PresentationModel->delete_presentation_by_id($this->input->post('removed'));
        redirect("user/user");
    }
}
