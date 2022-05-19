<?php
class PresentationModel extends CI_Model
{
    public function __construct()
    {
        $this->load->database();
    }

    public function get_all_presentations()
    {
        $query = $this->db->get('presentations');
        return $query->result_array();
    }

    public function get_presentation_by_id($id)
    {
        $query = $this->db->query("SELECT * FROM presentations WHERE id = ?", [$id]);
        return $query->row_array();
    }

    public function get_presentations_by_conference_id($id)
    {
        $query = $this->db->query("SELECT * FROM presentations WHERE conference_id = ? ORDER BY start ASC", [$id]);
        return $query->result_array();
    }

    public function get_confirmed_presentations_by_conference_id($id)
    {
        $query = $this->db->query("SELECT * FROM presentations WHERE conference_id = ? AND confirmed=1 ORDER BY start ASC", [$id]);
        return $query->result_array();
    }

    public function get_presentation_by_highest_id()
    {
        $query = $this->db->query("SELECT id FROM Presentations ORDER BY id DESC LIMIT 1");
        return $query->row_array();
    }

    public function insert_presentation($data)
    {
        $this->db->insert('presentations', $data);
    }

    public function update_presentation($data, $id)
    {
        $this->db->where('id', $id);
        $this->db->update('presentations', $data);
    }

    public function get_presentations_by_room_id($id)
    {
        $query = $this->db->get_where("presentations", ["room_id" => $id]);
        return $query->result_array();
    }

    public function update_multiple_presentations_by_id($data)
    {
        $this->db->update_batch('presentations', $data, 'id');
    }

    public function get_confirmed_presentations_with_rooms($id)
    {
        $query = $this->db->query('SELECT p.id, p.room_id, p.name, p.start, p.finish, r.name as "rname" FROM presentations p, rooms r WHERE p.room_id = r.id and p.confirmed = 1 and p.conference_id = ?', [$id]);
        return $query->result_array();
    }

    public function delete_presentation_by_id($id)
    {
        $this->db->delete('presentations', ['id' => $id]);
    }
}
