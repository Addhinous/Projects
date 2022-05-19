<?php
class ConferenceManagerController extends CI_Controller
{
    public function __construct()
    {

        parent::__construct();
        $this->load->helper(array('form', 'url'));
        $this->load->library(['form_validation']);
        $this->load->library('session');
        $this->load->database();

        $this->load->model('RoomModel');
        $this->load->model('PresentationModel');
        $this->load->model('Conference_model');
        $this->load->model('TicketModel');

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

    private function checkDateOverlap($startDate1, $endDate1, $startDate2, $endDate2)
    {
        return (strtotime($startDate1) < strtotime($endDate2)) and (strtotime($startDate2) < strtotime($endDate1));
    }

    public function ajaxDeletePlan()
    {
        if(!isset($_POST["id"]))
        {
            redirect('/');
        }
        $pres = $this->PresentationModel->get_presentation_by_id($_POST["id"]);
        $conf = $this->Conference_model->get_conference_by_id($pres["conference_id"]);
        if(!isset($_SESSION["id"]) || (($_SESSION["admin"] == "0") && ($_SESSION["id"] != $conf["user_id"])))
        {
            redirect('/');
        }
        $this->PresentationModel->update_presentation(["room_id" => NULL, "start" => NULL, "finish" => NULL], $_POST["id"]);
    }

    public function ajaxDeleteTicketByCode()
    {
        $this->TicketModel->delete_ticket_by_code($_POST["code"]);
    }

    public function ajaxDeleteRoomById()
    {
        if(!isset($_POST["id"]))
        {
            redirect('/');
        }
        $room = $this->RoomModel->get_room_by_id($_POST["id"]);
        $conf = $this->Conference_model->get_conference_by_id($room["conference_id"]);
        if(!isset($_SESSION["id"]) || (($_SESSION["admin"] == "0") && ($_SESSION["id"] != $conf["user_id"])))
        {
            redirect('/');
        }
        if ($this->PresentationModel->get_presentations_by_room_id($_POST["id"])) {
            echo json_encode("err");
        } else {
            $this->RoomModel->delete_room($_POST["id"]);
            echo json_encode("ok");
        }
    }

    public function confirmPresentation()
    {
        if(!isset($_POST["id"]))
        {
            redirect('/');
        }
        $conf = $this->Conference_model->get_conference_by_id($_POST["id"]);
        if(!isset($_SESSION["id"]) || (($_SESSION["admin"] == "0") && ($_SESSION["id"] != $conf["user_id"])))
        {
            redirect('/');
        }
        $allPresentations = $this->PresentationModel->get_presentations_by_conference_id($_POST["id"]);
        $updateData = [];
        foreach ($allPresentations as $key => $value) {
            if (isset($_POST[$value["id"]])) {
                $updateData[] = ["id" => $value["id"], "confirmed" => 1];
            } else {
                $updateData[] = ["id" => $value["id"], "confirmed" => 0, "start" => NULL, "finish" => NULL, "room_id" => NULL];
            }
        }
        $this->PresentationModel->update_multiple_presentations_by_id($updateData);
        redirect(base_url() . "managerTimePlanner?id=" . $_POST["id"]);
    }

    public function confirmReservation()
    {
        if(!isset($_POST["id"]))
        {
            redirect('/');
        }
        $conf = $this->Conference_model->get_conference_by_id($_POST["id"]);
        if(!isset($_SESSION["id"]) || (($_SESSION["admin"] == "0") && ($_SESSION["id"] != $conf["user_id"])))
        {
            redirect('/');
        }
        $tickets = $this->TicketModel->get_tickets_by_conference_id($_POST["id"]);
        $updateData = [];
        foreach ($tickets as $key => $value) {
            $updateData[] = ["id" => $value["id"], "paid" => isset($_POST[$value["code"]])];
        }
        $this->TicketModel->update_multiple_tickets_by_id($updateData);
        redirect(base_url() . "managerTimePlanner?id=" . $_POST["id"]);
    }

    public function timePlanner()
    {
        if(!isset($_GET["id"]))
        {
            redirect('/');
        }
        $conf = $this->Conference_model->get_conference_by_id($_GET["id"]);
        if(!isset($_SESSION["id"]) || (($_SESSION["admin"] == "0") && ($_SESSION["id"] != $conf["user_id"])))
        {
            redirect('/');
        }

        $data["rooms"] = $this->RoomModel->get_rooms_by_conference_id($_GET["id"]);
        $conference = $this->Conference_model->get_conference_by_id($_GET["id"]);
        $data["presentations"] = $this->PresentationModel->get_confirmed_presentations_by_conference_id($_GET["id"]);
        $data["allpresentations"] = $this->PresentationModel->get_presentations_by_conference_id($_GET["id"]);

        $data["plan"] = $this->PresentationModel->get_confirmed_presentations_with_rooms($_GET["id"]);
        $data["reservations"] = $this->TicketModel->get_tickets_by_conference_group_by_code($_GET["id"]);

        function cmp($a, $b)
        {
            return (int)$a["room_id"] > (int)$b["room_id"];
        }
        usort($data["plan"], "cmp");

        $this->form_validation->set_rules('selectPresentation', 'Presentation', 'required');
        $this->form_validation->set_rules('selectRoom', 'Room', 'required');
        $this->form_validation->set_rules('inputDateFrom', 'Date From', 'required');
        $this->form_validation->set_rules('inputDateTo', 'Date To', 'required');

        $this->load->view('templates/header');
        if ($this->form_validation->run() == false) {
            $this->load->view('pages/ManagerTimePlanner', $data);
            $this->load->view('templates/footer');
        } else {
            if (strtotime($_POST["inputDateFrom"]) < strtotime($conference["from"]) || strtotime($_POST["inputDateTo"]) > strtotime($conference["to"])) {
                $this->session->set_flashdata(
                    'conf_date_error',
                    'Presentations date is not in date of conference (' . $conference["from"] . ' - ' . $conference["to"] . ')'
                );

                $this->load->view('pages/ManagerTimePlanner', $data);
                $this->load->view('templates/footer');
                return;
            }
            if (strtotime($_POST["inputDateFrom"]) > strtotime($_POST["inputDateTo"])) {
                $this->session->set_flashdata('date_error', 'Presentation ends before it starts');

                $this->load->view('pages/ManagerTimePlanner', $data);
                $this->load->view('templates/footer');
                return;
            }
            foreach ($data["plan"] as $key => $value) {
                if ($value["room_id"] == $_POST["selectRoom"] && $value["id"] != $_POST["selectPresentation"]) {
                    if ($this->checkDateOverlap($_POST["inputDateFrom"], $_POST["inputDateTo"], $value["start"], $value["finish"])) {
                        $this->session->set_flashdata('room_error', 'Presentation overlaping with another in same room');

                        $this->load->view('pages/ManagerTimePlanner', $data);
                        $this->load->view('templates/footer');
                        return;
                    }
                }
            }
            $this->PresentationModel->update_presentation(["room_id" => $_POST["selectRoom"], "start" => $_POST["inputDateFrom"], "finish" => $_POST["inputDateTo"]], $_POST["selectPresentation"]);
            $data["plan"] = $this->PresentationModel->get_confirmed_presentations_with_rooms($_GET["id"]);
            usort($data["plan"], "cmp");
            $this->load->view('pages/ManagerTimePlanner', $data);
            $this->load->view('templates/footer');
        }
    }
}
