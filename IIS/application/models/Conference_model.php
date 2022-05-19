<?php
class Conference_model extends CI_Model
{
    public function __construct()
    {
        $this->load->database();
    }

    public function get_all_conferences()
    {
        $query = $this->db->get('conferences');
        return $query->result_array();
    }

    public function get_conference_by_userId_and_conferenceId($userId, $onferenceId)
    {
        $query = $this->db->query("SELECT * FROM conferences WHERE id = ? and user_id = ?", [$onferenceId, $userId]);
        return $query->row_array();
    }

    public function get_conference_by_id($id)
    {
        $query = $this->db->query("SELECT * FROM conferences WHERE id = ?", [$id]);
        return $query->row_array();
    }

    public function get_conference_by_highest_id()
    {
        $query = $this->db->query("SELECT id FROM conferences ORDER BY id DESC LIMIT 1");
        return $query->row_array();
    }

    public function get_count_of_tickets_on_conference($id)
    {
        $query = $this->db->query('SELECT count(user_id) as "count" FROM tickets WHERE conference_id = ?', [$id]);
        return $query->row_array();
    }

    public function get_user_by_email($email)
    {
        return $this->db->get_where('users', ['email' => $email])->row();
    }

    public function add_user($email, $name, $surename, $password)
    {
        $this->db->insert("users", ["email" => $email, "name" => $name, "surename" => $surename, "password" => $password]);
    }

    public function get_sold_tickets_count_by_conference_id($id)
    {
        $query = $this->db->query("SELECT COUNT(*) AS sold FROM tickets WHERE conference_id = ?", [$id]);
        return $query->row_array();
    }

    public function insert_conference($data)
    {
        $this->db->insert('conferences', $data);
    }

    public function update_conference($data, $id)
    {
        $this->db->where('id', $id);
        $this->db->update('conferences', $data);
    }

    public function delete_conference_by_id($id)
    {
        $this->db->delete('conferences', ['id' => $id]);
    }

    public function get_all_countries()
    {
        return $this->db->query("SELECT * FROM countries")->result_array();
    }
}
