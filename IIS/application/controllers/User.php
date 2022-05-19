<?php
class User extends CI_Controller
{
    public function __construct()
    {

        parent::__construct();
        $this->load->helper(array('form', 'url'));
        $this->load->library('session');
        $this->load->model('user_model');
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

    public function user()
    {
        if (!$this->session->has_userdata("id")) {
            redirect('/');
        }

        $data["tickets"] = $this->user_model->get_tickets_by_user_id_groub_by_code(intval($this->session->userdata["id"]));
        $data["conferences"] = $this->user_model->get_conferences_by_user_id(intval($this->session->userdata["id"]));
        foreach ($data["conferences"] as $key => $value) {
            $data["conferences"][$key]["reserved"] = $this->user_model->get_ticket_count_by_conference_id($value["id"])->count;
        }
        $data["presentations"] = $this->user_model->get_presentations_by_user_id(intval($this->session->userdata["id"]));

        if ($this->session->userdata["admin"]) {
            $data["users"] = $this->user_model->get_all_users();
        }

        $this->load->view('templates/header');
        $this->load->view('pages/user', $data);
        $this->load->view('templates/footer');
    }

    public function ajaxGetUserById()
    {
        if (isset($_SESSION["admin"]) && $_SESSION["admin"] == 1) {
            echo json_encode($this->user_model->get_user_by_id($_POST["id"]));
        }
    }

    public function ajaxGetUserBySessionId()
    {
        if (isset($_SESSION["id"])) {
            echo json_encode($this->user_model->get_user_by_id($_SESSION["id"]));
        }
    }

    public function ajaxUpdateUserById()
    {
        if (isset($_SESSION["admin"]) && $_SESSION["admin"] == 1) {
            if ($this->user_model->get_user_by_id($_POST["id"])->email != $_POST["email"] && $this->user_model->get_user_by_email($_POST["email"]) != null) {
                echo json_encode("err-email");
                return;
            }
            $newData = ["name" => $_POST["name"], "surename" => $_POST["surename"], "email" => $_POST["email"], "is_admin" => (int)$_POST["admin"], "is_deactivated" => (int)$_POST["deactivated"]];
            $this->user_model->update_user_by_id($_POST["id"], $newData);
            echo json_encode($this->user_model->get_all_users());
        }
    }

    public function ajaxDeleteUserById()
    {
        if (isset($_SESSION["admin"]) && $_SESSION["admin"] == 1) {
            $this->user_model->delete_user_by_id($_POST["id"]);
            echo json_encode($this->user_model->get_all_users());
        }
    }

    public function ajaxUpdateUserInfoById()
    {
        if (isset($_SESSION["id"])) {
            $user = $this->user_model->get_user_by_email($_SESSION["email"]);
            $newData = ["name" => $_POST["name"], "surename" => $_POST["surename"], "email" => $_POST["email"]];
            if ($_SESSION["email"] != $_POST["email"] && $this->user_model->get_user_by_email($_POST["email"]) != null) {
                echo json_encode("err-email");
                return;
            }
            if ($_POST["changepass"] == "true") {
                if (!password_verify($_POST["oldpass"], $user->password)) {
                    echo json_encode("err-pass");
                    return;
                } else {
                    $newData["password"] = password_hash($_POST["newpass"], PASSWORD_DEFAULT);
                }
            }
            $_SESSION["name"] = $_POST["name"];
            $_SESSION["surename"] = $_POST["surename"];
            $_SESSION["email"] = $_POST["email"];
            $this->user_model->update_user_by_id($_SESSION["id"], $newData);
            echo json_encode("ok");
        }
    }
}
