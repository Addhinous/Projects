<?php
class ReservationController extends CI_Controller
{
    public function __construct()
    {

        parent::__construct();
        $this->load->model('user_model');
        $this->load->model('TicketModel');
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

    public function reserveTickets()
    {
        $this->load->model('Conference_model');
        if (!isset($_GET['reserve']) || (($conf = $this->Conference_model->get_conference_by_id($_GET['reserve'])) == NULL)) {
            redirect('/');
        }

        $this->load->view('templates/header');


        $this->form_validation->set_rules('num_tickets', 'Number of tickets', 'required');

        $code = "";
        while (1) {
            $code = bin2hex(random_bytes(5));
            if (!$this->TicketModel->get_ticket_by_code($code)) {
                break;
            }
        }

        if ($this->session->has_userdata("email")) {
            if ($this->form_validation->run() == false) {
                $this->load->view('pages/reserveTicketsLogged');
                return;
            } else {
                $id = $_SESSION["id"];
                $name = $_SESSION["name"];
                $surename = $_SESSION["surename"];
                $email = $_SESSION["email"];
                $num_tickets = $this->input->post('num_tickets');
                $rem = $conf["capacity"] - $this->Conference_model->get_sold_tickets_count_by_conference_id($conf["id"])["sold"];
                $data["num_tickets"] = $num_tickets;
                $data["name"] = $name;
                $data["surename"] = $surename;
                $data["email"] = $email;
                if ($num_tickets > $rem) {
                    $this->session->set_flashdata('number_error', 'Please, select a number of tickets within the available capacity of the conference');
                    $this->load->view('pages/reserveTicketsLogged');
                    $this->load->view('templates/footer');
                    return;
                }
                $conference_id = $_GET['reserve'];
                for ($i = 0; $i < $num_tickets; $i++) {
                    $this->TicketModel->add_ticketR($email, $name, $surename, $code, $conference_id, $id);
                }
            }
        } else {

            $this->form_validation->set_rules('email', 'Email', 'required');
            $this->form_validation->set_rules('name', 'Name', 'required');
            $this->form_validation->set_rules('surename', 'Surename', 'required');
            if ($this->form_validation->run() == false) {
                $this->load->view('pages/reserveTickets');
                return;
            } else {
                $name = $this->input->post('name');
                $surename = $this->input->post('surename');
                $email = $this->input->post('email');
                $num_tickets = $this->input->post('num_tickets');
                $rem = $conf["capacity"] - $this->Conference_model->get_sold_tickets_count_by_conference_id($conf["id"])["sold"];
                $data["num_tickets"] = $num_tickets;
                $data["name"] = $name;
                $data["surename"] = $surename;
                $data["email"] = $email;
                if ($num_tickets > $rem) {
                    $this->session->set_flashdata('number_error', 'Please, select a number of tickets within the available capacity of the conference');
                    $this->load->view('pages/reserveTickets');
                    $this->load->view('templates/footer');
                    return;
                }
                $conference_id = $_GET['reserve'];

                for ($i = 0; $i < $num_tickets; $i++) {
                    $this->TicketModel->add_ticket($email, $name, $surename, $code, $conference_id);
                }
            }
        }
        $data["code"] = $code;
        // $this->load->library('email');
        // $config['useragent'] = 'CodeIgniter';
        // $config['protocol'] = "smtp";
        // $config['smtp_host'] = 'ssl://smtp.googlemail.com';
        // $config['smtp_port'] = 465;
        // $config['smtp_timeout'] = 5;

        // $config['smtp_user'] = 'iisconferencemanager@gmail.com';
        // $config['smtp_pass'] = 'iisconference';
        // $config['charset'] = 'utf-8';
        // $config['newline'] = "\r\n";
        // $config['mailtype'] = 'html';
        // $config['validate'] = FALSE;
        // $this->email->initialize($config);
        // $this->email->set_mailtype("html");
        // $this->email->from('iisconferencemanager@gmail.com', 'iisconferencemanager@gmail.com');
        // $this->email->to('marhefka.adam99@gmail.com');
        // $this->email->subject('Email Test');
        // $this->email->message('Testing the email class.');

        // $returnval = $this->email->send();
        // echo $returnval;
        // echo "adamec".$returnval;
        $this->load->view('pages/TicketView', $data);
        $this->load->view('templates/footer');
    }

    public function removeTicket()
    {
        if (!isset($_POST["removed"])) {
            redirect("/");
        }
        $ticket = $this->TicketModel->get_ticket_by_code($_POST["removed"]);
        if (!$ticket || ($ticket["user_id"] != $_SESSION["id"] && $_SESSION["admin"] != "1")) {
            redirect("/");
        }
        $this->TicketModel->delete_ticket_by_code($this->input->post('removed'));
        redirect("user/user");
    }
}
