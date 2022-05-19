<?php
class TicketModel extends CI_Model
{
    public function __construct()
    {
        $this->load->database();
    }

    public function get_all_tickets()
    {
        $query = $this->db->get('tickets');
        return $query->result_array();
    }

    public function get_ticket_by_code($code)
    {
        $query = $this->db->get_where('tickets', ['code' => $code]);
        return $query->row_array();
    }

    public function get_tickets_by_conference_group_by_code($conference_id)
    {
        $query =  $this->db->query('SELECT u.name, t.created, u.surename, u.email, t.code, t.paid, count(t.code) as "count" FROM tickets t iNNER JOIN users u ON u.id = t.user_id WHERE t.conference_id = ? Group by t.code', [$conference_id]);
        return $query->result_array();
    }

    public function get_tickets_by_conference_id($id)
    {
        $query = $this->db->get_where('tickets', ['conference_id' => $id]);
        return $query->result_array();
    }

    public function add_ticket($email, $name, $surename, $code, $conference_id)
    {
        $this->db->insert("tickets", ["email" => $email, "name" => $name, "surename" => $surename, "code" => $code, "conference_id" => $conference_id]);
    }

    public function add_ticketR($email, $name, $surename, $code, $conference_id, $user_id)
    {
        $this->db->insert("tickets", ["email" => $email, "name" => $name, "surename" => $surename, "code" => $code, "conference_id" => $conference_id, "user_id" => $user_id]);
    }

    public function delete_ticket_by_id($id)
    {
        $this->db->delete('tickets', ['id' => $id]);
    }

    public function delete_ticket_by_code($code)
    {
        $this->db->delete('tickets', ['code' => $code]);
    }

    public function update_multiple_tickets_by_id($data)
    {
        $this->db->update_batch('tickets', $data, 'id');
    }
}
