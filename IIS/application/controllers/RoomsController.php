<?php
class RoomsController extends CI_Controller
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

    public function create()
    {
        if ((!isset($_GET["id"]) && !isset($_POST["submit"])) || !isset($_SESSION["id"])) {
            redirect("/");
        }

        $id = isset($_GET["id"]) ? $_GET["id"] : $_POST["submit"];
        $data["id"] = $id;

        $this->load->model('Conference_model');
        if (!$this->Conference_model->get_conference_by_userId_and_conferenceId($_SESSION["id"], $id) && !intval($_SESSION["admin"])) {
            redirect("/");
        }
        if (!$this->Conference_model->get_conference_by_id($id)) {
            redirect("/");
        }

        $this->form_validation->set_rules('name', 'Name', 'required');
        $this->form_validation->set_rules('city', 'City', 'required');
        $this->form_validation->set_rules('street', 'Street', 'required');
        $this->form_validation->set_rules('postcode', 'Post code', 'required');
        $this->form_validation->set_rules('streetNumber', 'Street number', 'required');

        if ($this->form_validation->run() == false) {
            $this->load->view('templates/header');
            $this->load->view('pages/RoomCreateView', $data);
            $this->load->view('templates/footer');
        } else {
            $this->load->model('RoomModel');
            $this->RoomModel->insert_room(["conference_id" => $id, "description" => $_POST["description"], "name" => $_POST["name"], "city" => $_POST["city"], "street" => $_POST["street"], "postcode" => $_POST["postcode"], "street_number" => $_POST["streetNumber"]]);
            $this->session->set_flashdata('success', 'Room created');
            redirect(base_url() . "managerTimePlanner?id=" . $id);
        }
    }

    public function edit()
    {
        if ((!isset($_GET["id"]) && !isset($_POST["submit"])) || !isset($_SESSION["id"])) {
            redirect("/");
        }
        
        $id = isset($_GET["id"]) ? $_GET["id"] : $_POST["submit"];
        $data["id"] = $id;

        $this->form_validation->set_rules('name', 'Name', 'required');
        $this->form_validation->set_rules('city', 'City', 'required');
        $this->form_validation->set_rules('street', 'Street', 'required');
        $this->form_validation->set_rules('postcode', 'Post code', 'required');
        $this->form_validation->set_rules('streetNumber', 'Street number', 'required');

        $this->load->model('RoomModel');
        $data["room"] = $this->RoomModel->get_room_by_id($id);
        if ($this->form_validation->run() == false) {
            $this->load->view('templates/header');
            $this->load->view('pages/RoomEditView', $data);
            $this->load->view('templates/footer');
        } else {

            $this->RoomModel->update_room(["description" => $_POST["description"], "name" => $_POST["name"], "city" => $_POST["city"], "street" => $_POST["street"], "postcode" => $_POST["postcode"], "street_number" => $_POST["streetNumber"]], $id);
            redirect(base_url() . "managerTimePlanner?id=" . $data["room"]["conference_id"]);
        }
    }
}
