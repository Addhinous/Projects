<?php
class UserAccessController extends CI_Controller
{
    public function __construct()
    {

        parent::__construct();
        $this->load->helper(array('form', 'url'));
        $this->load->model('user_model');
        $this->load->library(['form_validation']);
        $this->load->library('session');
        $this->load->database();
        $this->autologout();
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

    private function redirect_if_logged()
    {
        if ($this->session->has_userdata("email")) {
            redirect('/');
        }
    }

    public function reservation_with_registration()
    {
    }

    private function validatePassword($pass)
    {
        return preg_match("/[a-z]/", $pass) && preg_match("/[A-Z]/", $pass) && preg_match("/[0-9]/", $pass) && strlen($pass) >= 6;
    }

    public function registration()
    {
        $this->redirect_if_logged();
        $this->form_validation->set_rules('email', 'Email', 'required');
        $this->form_validation->set_rules('password', 'Password', 'required');
        $this->form_validation->set_rules('name', 'Name', 'required');
        $this->form_validation->set_rules('surename', 'Surename', 'required');
        $this->form_validation->set_rules('passwordAgain', 'Password again', 'required');

        $data["url"] = "";
        if ($this->input->post('conference_id')) {
            $data["url"] = "registration?conference_id=" . $this->input->post('conference_id');
        }

        else if(isset($_GET["conference_id"])){
            $data["url"] = "registration?conference_id=" . $_GET["conference_id"];
        }
        
        else{
            $data["url"] = "registration";
        }

        $this->load->view('templates/header');
        if ($this->form_validation->run() == false) {
            $this->load->view('pages/registration', $data);
        } else {
            $email = $this->input->post('email');
            $password = $this->input->post('password');
            $passwordAgain = $this->input->post('passwordAgain');
            $name = $this->input->post('name');
            $surename = $this->input->post('surename');

            if ($this->user_model->get_user_by_email($email)) {
                $this->session->set_flashdata('registration_error', 'Account with this email already exists.', 300);
                $this->load->view('pages/registration', $data);
                $this->load->view('templates/footer');
                return;
            } elseif (!$this->validatePassword($this->input->post('password'))) {
                $this->session->set_flashdata('registration_error', 'Passwords have to be at least 6 charackter long and contain big character, small characket and number.', 300);
                $this->load->view('pages/registration', $data);
                $this->load->view('templates/footer');
            } elseif ($password !== $passwordAgain) {
                $this->session->set_flashdata('registration_error', 'Passwords are not same.', 300);
                $this->load->view('pages/registration', $data);
                $this->load->view('templates/footer');
                return;
            } else {
                $insertedId = $this->user_model->add_user($email, $name, $surename, password_hash($password, PASSWORD_DEFAULT));
                $this->session->set_userdata(['id' => $insertedId, 'name' => $name, 'surename' => $surename, 'email' => $email, "admin" => "0", "last_login_timestamp" => time(), "justloggedin" => true]);

                if ($this->input->post('conference_id')) {
                    redirect('reserveTickets?reserve=' . $this->input->post('conference_id'));
                }

                redirect('/');
            }
        }
    }

    public function login()
    {
        $this->redirect_if_logged();

        $this->form_validation->set_rules('email', 'Email', 'required');
        $this->form_validation->set_rules('password', 'Password', 'required');

        $this->load->view('templates/header');
        if ($this->form_validation->run() == false) {
            $this->load->view('pages/login');
        } else {
            $email = $this->input->post('email');
            $password = $this->input->post('password');

            $user = $this->user_model->get_user_by_email($email);

            if (!$user) {
                $this->session->set_flashdata('login_error', 'Please check your email or password and try again.', 300);
                $this->load->view('pages/login');
                $this->load->view('templates/footer');
                return;
            }

            if (!password_verify($password, $user->password)) {
                $this->session->set_flashdata('login_error', 'Please check your email or password and try again.', 300);
                $this->load->view('pages/login');
                $this->load->view('templates/footer');
                return;
            }
            if (intval($user->is_deactivated)) {
                $this->session->set_flashdata('login_error_deactivated', true);
                redirect('/');
            }

            $this->session->set_userdata(['admin' => $user->is_admin, 'id' => $user->id, 'name' => $user->name, "last_login_timestamp" => time(), 'surename' => $user->surename, 'email' => $user->email, "justloggedin" => true]);
            redirect('/');
        }
        $this->load->view('templates/footer');
    }

    public function logout()
    {
        $this->session->sess_destroy();
        redirect('/', 'refresh');
    }
}
