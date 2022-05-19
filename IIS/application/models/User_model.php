<?php
class User_model extends CI_Model
{
    public function __construct()
    {
        $this->load->database();
    }

    public function get_user_by_email($email)
    {
        return $this->db->get_where('users', ['email' => $email])->row();
    }

    public function add_user($email, $name, $surename, $password)
    {
        $this->db->insert("users", ["email" => $email, "name" => $name, "surename" => $surename, "password" => $password]);
        return $this->db->insert_id();
    }

    public function get_tickets_by_user_id($id)
    {
        return $this->db->query('SELECT c.name, c.image, c.from, c.to, t.code, c.id, t.id as "tid", count(t.conference_id) as "count" FROM tickets t iNNER JOIN conferences c ON t.conference_id = c.id WHERE t.user_id = ? Group by t.conference_id', [$id])->result_array();
    }

    public function get_tickets_by_user_id_groub_by_code($id)
    {
        $query = $this->db->query('SELECT c.name, t.paid, c.image, c.from, c.to, t.code, c.id, t.id as "tid", count(t.code) as "count" FROM tickets t iNNER JOIN conferences c ON t.conference_id = c.id WHERE t.user_id = ? Group by t.code', [$id]);
        return $query->result_array();
    }

    public function get_conferences_by_user_id($id)
    {
        return $this->db->query('SELECT c.id, c.name, c.image, c.from, c.to, c.capacity FROM conferences c JOIN genres g ON c.genre_id=g.id WHERE c.user_id= ?', [$id])->result_array();
    }

    public function get_ticket_count_by_conference_id($id)
    {
        return $this->db->query('SELECT count(*) as "count" FROM tickets WHERE conference_id = ?', [$id])->row();
    }

    public function get_presentations_by_user_id($id)
    {
        return $this->db->query('SELECT p.name "p_name", p.id, p.start, p.finish, p.conference_id, c.name "c_name", p.confirmed FROM presentations p JOIN conferences c on c.id=p.conference_id WHERE p.user_id = ?', [$id])->result_array();
    }

    public function get_all_users()
    {
        return $this->db->query('SELECT u.id, u.is_deactivated, u.email, u.name, u.surename, u.is_admin, count(c.user_id) "conferences", count(p.user_id) "presentations" FROM users u left join presentations p on p.user_id = u.id left join conferences c on c.user_id = u.id group by u.name')->result_array();
    }

    public function get_user_by_id($id)
    {
        return $this->db->get_where('users', ['id' => $id])->row();
    }

    public function update_user_by_id($id, $data)
    {
        $this->db->where('id', $id);
        $this->db->update('users', $data);
    }

    public function delete_user_by_id($id)
    {
        $this->db->delete('users', ['id' => $id]);
    }
}
